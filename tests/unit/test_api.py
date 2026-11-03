"""Prototype UI API: catalog, validation, auth, submission (with a fake sbatch/sacct on PATH), job isolation."""
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "lib"))

TOKEN_A = "un=alice@patricbrc.org|tokenid=x|expiry=9999999999|sig=abc"
TOKEN_B = "un=bob@patricbrc.org|tokenid=y|expiry=9999999999|sig=def"


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.old_env = {k: os.environ.get(k) for k in ("MODPIPE_UI_STATE", "PATH")}
        os.environ["MODPIPE_UI_STATE"] = os.path.join(cls.tmp, "state")
        bindir = os.path.join(cls.tmp, "bin")
        os.makedirs(bindir)
        with open(os.path.join(bindir, "sbatch"), "w") as f:      # records its args, prints a job id
            f.write(f"#!/bin/bash\necho \"$@\" >> {cls.tmp}/sbatch.calls\necho 4242\n")
        with open(os.path.join(bindir, "sacct"), "w") as f:
            f.write("#!/bin/bash\necho '4242|COMPLETED|00:00:10|0:0|node1'\n")
        for x in ("sbatch", "sacct"):
            os.chmod(os.path.join(bindir, x), 0o755)
        os.environ["PATH"] = bindir + os.pathsep + os.environ["PATH"]
        import importlib
        import modpipe.api as api
        importlib.reload(api)                                      # pick up MODPIPE_UI_STATE
        cls.api = api
        cls.httpd = api.ThreadingHTTPServer(("127.0.0.1", 0), api.make_handler(api.Catalog(), {"http://localhost:3000"}))
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        for k, v in cls.old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(cls.tmp)

    def call(self, method, path, body=None, token=None, origin=None):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", method=method,
                                     data=json.dumps(body).encode() if body is not None else None)
        req.add_header("Content-Type", "application/json")
        if token:
            req.add_header("Authorization", token)
        if origin:
            req.add_header("Origin", origin)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, json.loads(r.read()), dict(r.headers)
        except urllib.error.HTTPError as e:
            with e:
                return e.code, json.loads(e.read()), dict(e.headers)

    def test_templates_and_sources(self):
        st, rows, _ = self.call("GET", "/api/templates")
        self.assertEqual(st, 200)
        t = {r["template"]: r for r in rows}
        self.assertIn("sars2_consensus", t)
        kinds = {o["kind"] for o in t["sars2_consensus"]["inputs"][0]["source_options"]}
        self.assertEqual(kinds, {"paired_end_libs", "srr_ids"})
        ref = [i for i in t["sars2_consensus"]["inputs"] if i["name"] == "reference"][0]
        self.assertEqual(ref["default_source"], {"database_file": "artic_v4.1:reference"})
        db = [p for p in t["sars2_consensus"]["params"] if p["key"] == "primertrim.params.primers"][0]
        self.assertIn("artic_v4.1", [c["value"] for c in db["choices"]])

    def test_cors(self):
        _, _, h = self.call("GET", "/api/health", origin="http://localhost:3000")
        self.assertEqual(h.get("Access-Control-Allow-Origin"), "http://localhost:3000")
        _, _, h = self.call("GET", "/api/health", origin="http://evil.example")
        self.assertNotIn("Access-Control-Allow-Origin", h)

    def test_instantiate_and_validate(self):
        st, r, _ = self.call("POST", "/api/instantiate", {"template": "align_and_tree",
                                                           "inputs": {"proteins": {"feature_ids": ["fig|1206109.14.peg.1"]}}})
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["resources"]["cpu"], 8)
        st, r, _ = self.call("POST", "/api/instantiate", {"template": "align_and_tree", "inputs": {}})
        self.assertFalse(r["ok"])
        self.assertIn("not supplied", r["errors"][0])
        st, r, _ = self.call("POST", "/api/validate", {"pipeline": {"schema": "modpipe/pipeline/v1", "steps": {}}})
        self.assertFalse(r["ok"])

    def test_submit_auth_and_isolation(self):
        body = {"template": "align_and_tree", "inputs": {"proteins": {"feature_ids": ["fig|1206109.14.peg.1"]}},
                "output_path": "/alice@patricbrc.org/home/tests", "output_file": "tree1"}
        st, r, _ = self.call("POST", "/api/submit", body)
        self.assertEqual(st, 401)
        st, r, _ = self.call("POST", "/api/submit", {**body, "output_file": "bad;name"}, token=TOKEN_A)
        self.assertEqual(st, 400)
        st, r, _ = self.call("POST", "/api/submit", body, token=TOKEN_A)
        self.assertEqual(st, 200, r)
        jid = r["job"]["id"]
        jdir = os.path.join(os.environ["MODPIPE_UI_STATE"], "jobs", jid)
        self.assertEqual(os.stat(os.path.join(jdir, "token")).st_mode & 0o777, 0o600)
        with open(os.path.join(jdir, "token")) as f:
            self.assertEqual(f.read(), TOKEN_A)
        with open(os.path.join(self.tmp, "sbatch.calls")) as f:
            calls = f.read()
        self.assertNotIn("tokenid", calls)                       # token never on the sbatch command line
        self.assertIn("--cpus-per-task 8", calls)
        st, jobs, _ = self.call("GET", "/api/jobs", token=TOKEN_A)
        self.assertEqual([j["id"] for j in jobs], [jid])
        self.assertEqual(jobs[0]["state"], "COMPLETED")
        st, jobs, _ = self.call("GET", "/api/jobs", token=TOKEN_B)   # bob sees nothing of alice's
        self.assertEqual(jobs, [])
        st, r, _ = self.call("GET", f"/api/jobs/{jid}/log", token=TOKEN_B)
        self.assertEqual(st, 404)

    def test_invalid_pipeline_rejected_before_sbatch(self):
        body = {"pipeline": {"schema": "modpipe/pipeline/v1", "name": "x",
                             "inputs": {"p": {"type": "sequences.protein", "source": {"feature_ids": ["fig|1.1.peg.1"]}}},
                             "steps": {"t": {"module": "fasttree", "in": {"alignment": "$inputs.p"}}}, "outputs": {"t": "t.tree"}},
                "output_path": "/alice@patricbrc.org/home", "output_file": "x"}
        st, r, _ = self.call("POST", "/api/submit", body, token=TOKEN_A)
        self.assertEqual(st, 400)
        self.assertTrue(any("type mismatch" in e for e in r["errors"]))


if __name__ == "__main__":
    unittest.main()
