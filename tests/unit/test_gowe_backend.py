"""The API's GoWe backend (lib/modpipe/gowe_backend.py) against a stub GoWe server."""
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "lib"))

from modpipe import gowe_backend as gb  # noqa: E402
from modpipe.api import Catalog  # noqa: E402
from modpipe.cwl import export  # noqa: E402

TOKEN = "un=tester@bvbrc|tokenid=x|sig=fake"


class Stub(BaseHTTPRequestHandler):
    calls = []
    sub = {}

    def log_message(self, *a):
        pass

    def _reply(self, code, data=None, error=None):
        body = json.dumps({"status": "ok" if code < 400 else "error", "data": data, "error": error}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(n)) if n else None
        Stub.calls.append((self.command, self.path, self.headers.get("Authorization"), body))
        if self.headers.get("Authorization") != f"Bearer {TOKEN}":
            return self._reply(401, error={"code": "UNAUTHORIZED", "message": "bad token"})
        if self.command == "POST" and self.path == "/api/v1/workflows/":
            return self._reply(201, {"id": "wf_1"})
        if self.command == "POST" and self.path == "/api/v1/submissions/":
            if "bogus" in json.dumps(body):
                return self._reply(422, error={"code": "VALIDATION", "message": "nope", "details": [{"field": "x"}]})
            return self._reply(201, {"id": "sub_1"})
        if self.command == "GET" and self.path == "/api/v1/submissions/sub_1":
            return self._reply(200, Stub.sub)
        if self.command == "GET" and self.path == "/api/v1/submissions/sub_1/tasks/":
            return self._reply(200, [{"id": "t2", "step_id": "tree", "state": "PENDING"},
                                     {"id": "t1", "step_id": "align", "state": "FAILED",
                                      "started_at": "2026-11-13T19:29:35Z", "completed_at": "2026-11-13T19:30:38Z",
                                      "outputs": {"alignment": "/u@bvbrc/home/out/r/.align/alignment", "log": None}}])
        if self.command == "PUT" and self.path == "/api/v1/submissions/sub_1/cancel":
            return self._reply(200, {"id": "sub_1", "state": "CANCELLED"})
        if self.command == "GET" and self.path == "/api/v1/submissions/sub_1/tasks/t1/logs":
            return self._reply(200, {"stdout": "INFO: noise\nhello", "stderr": "boom", "exit_code": 2})
        return self._reply(404, error={"code": "NOT_FOUND", "message": self.path})

    do_GET = do_POST = do_PUT = _handle


class GoweBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Stub)
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
        cls.server = f"http://127.0.0.1:{cls.httpd.server_port}"
        cls.tmp = tempfile.mkdtemp()
        cls.cat = Catalog()
        tools = os.path.join(cls.tmp, "base", "current", "cwl", "tools")
        export(cls.cat.mods, cls.cat.ts, cls.cat.dbs, tools, image="/img/x.sif", modpipe_home="/release")
        cls.old_base = os.environ.get("MODPIPE_RELEASE_BASE")
        os.environ["MODPIPE_RELEASE_BASE"] = os.path.join(cls.tmp, "base")

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        shutil.rmtree(cls.tmp)
        if cls.old_base is None:
            os.environ.pop("MODPIPE_RELEASE_BASE", None)
        else:
            os.environ["MODPIPE_RELEASE_BASE"] = cls.old_base

    def setUp(self):
        Stub.calls.clear()
        self._ws = gb.ws_exists
        gb.ws_exists = lambda token, path: False                            # no Workspace in unit tests

    def tearDown(self):
        gb.ws_exists = self._ws

    def pipeline(self):
        with open(os.path.join(REPO, "tests", "gowe", "gowe_align_tree.json")) as f:
            return json.load(f)

    def test_run_name(self):
        self.assertEqual(gb.run_name_for("ui gowe align (1)"), "ui_gowe_align_1")
        self.assertEqual(gb.run_name_for("(x)"), "x")
        self.assertTrue(gb.run_name_for("__")[0].isalnum())

    def test_submit(self):
        if not os.access(os.path.join(gb.GOWE_DIR, "bin", "gowe"), os.X_OK):
            self.skipTest("gowe CLI not found (set GOWE_DIR)")
        jdir = os.path.join(self.tmp, "job1")
        os.makedirs(jdir)
        f = gb.submit(self.server, self.cat, self.pipeline(), "/u@bvbrc/home/out/", "my run", TOKEN, jdir)
        self.assertEqual((f["gowe_submission"], f["gowe_workflow"], f["run_name"]), ("sub_1", "wf_1", "my_run"))
        self.assertEqual(f["steps"], ["align", "tree"])
        self.assertEqual(f["result_folder"], "/u@bvbrc/home/out/my_run")       # one folder per run
        (m1, p1, a1, b1), (m2, p2, a2, b2) = Stub.calls
        self.assertEqual((m1, p1, a1), ("POST", "/api/v1/workflows/", f"Bearer {TOKEN}"))
        self.assertEqual(b1["name"], "modpipe-gowe-test-align-and-tree")
        self.assertIn("$graph", b1["cwl"])                                  # packed by gowe bundle
        self.assertEqual(b2["workflow_id"], "wf_1")
        self.assertEqual(b2["inputs"]["output_path"], "/u@bvbrc/home/out/my_run")
        self.assertNotIn("run_name", b2["inputs"])
        self.assertEqual(b2["inputs"]["proteins"]["type"], "sequences.protein")
        for root, _, files in os.walk(jdir):                               # the token is never written
            for n in files:
                with open(os.path.join(root, n), errors="replace") as fh:
                    self.assertNotIn("sig=fake", fh.read())

    def test_errors(self):
        with self.assertRaises(gb.GoweError) as c:
            gb._call(self.server, "GET", "/api/v1/submissions/sub_1", "wrong")
        self.assertEqual(c.exception.status, 401)
        with self.assertRaises(gb.GoweError) as c:
            gb._call(self.server, "POST", "/api/v1/submissions/", TOKEN, {"bogus": 1})
        self.assertEqual(c.exception.status, 502)
        self.assertIn("nope", c.exception.msg)
        self.assertEqual(c.exception.extra["gowe_details"], [{"field": "x"}])
        with self.assertRaises(gb.GoweError) as c:
            gb._call("http://127.0.0.1:1", "GET", "/x", TOKEN, timeout=2)
        self.assertIn("unreachable", c.exception.msg)
        if os.access(os.path.join(gb.GOWE_DIR, "bin", "gowe"), os.X_OK):
            gb.ws_exists = lambda token, path: path == "/u@bvbrc/home/out/taken"
            with self.assertRaises(gb.GoweError) as c:
                gb.submit(self.server, self.cat, self.pipeline(), "/u@bvbrc/home/out", "taken", TOKEN, self.tmp)
            self.assertEqual(c.exception.status, 409)
            self.assertIn("already exists", c.exception.msg)
        Stub.calls.clear()
        p = self.pipeline()
        p["inputs"]["proteins"]["source"] = {"fixture": "x"}
        with self.assertRaises(gb.GoweError) as c:
            gb.submit(self.server, self.cat, p, "/u@bvbrc/home/out", "r", TOKEN, self.tmp)
        self.assertEqual(c.exception.status, 400)
        self.assertTrue(any("fixture" in e for e in c.exception.extra["errors"]))
        self.assertEqual(Stub.calls, [])                                   # refused before contacting GoWe

    def test_status_and_log(self):
        job = {"gowe_submission": "sub_1", "steps": ["align", "tree"]}
        Stub.sub = {"state": "RUNNING", "created_at": "2026-11-13T19:29:33.616794008Z", "completed_at": None,
                    "task_summary": {"total": 2, "success": 1, "failed": 0},
                    "outputs": {"alignment": "/u@bvbrc/home/.r_align/alignment", "tree": None}}
        st = gb.status(self.server, job, TOKEN)
        self.assertEqual((st["state"], st["steps_done"], st["steps_total"]), ("RUNNING", 1, 2))
        self.assertEqual(st["outputs"], {"alignment": "/u@bvbrc/home/.r_align/alignment"})
        self.assertRegex(st["elapsed"], r"^\d+:\d\d:\d\d$")
        Stub.sub = dict(Stub.sub, state="SCHEDULED")
        self.assertEqual(gb.status(self.server, job, TOKEN)["state"], "PENDING")
        self.assertEqual(gb.status(self.server, job, "wrong")["state"], "UNKNOWN")
        text = gb.log(self.server, job, TOKEN)
        lines = text.splitlines()
        self.assertTrue(lines[0].startswith("=== align  FAILED"))           # workflow order, not server order
        self.assertIn("hello", lines)
        self.assertIn("boom", lines)
        self.assertNotIn("INFO: noise", text)
        self.assertIn("[exit code 2]", lines)
        self.assertIn("(not started)", lines)

    def test_detail_and_cancel(self):
        job = {"gowe_submission": "sub_1", "steps": ["align", "tree"], "result_folder": "/u@bvbrc/home/out/r",
               "pipeline": {"steps": {"align": {"module": "mafft"}, "tree": {"module": "fasttree"}}}}
        Stub.sub = {"state": "FAILED", "created_at": "2026-11-13T19:29:33Z", "completed_at": "2026-11-13T19:30:40Z",
                    "task_summary": {"total": 2, "success": 0, "failed": 1}, "outputs": {}}
        d = gb.detail(self.server, job, TOKEN)
        self.assertEqual(d["state"], "FAILED")
        a, t = d["step_detail"]
        self.assertEqual((a["id"], a["module"], a["state"], a["elapsed"]), ("align", "mafft", "FAILED", "0:01:03"))
        self.assertEqual(a["outputs"], {"alignment": "/u@bvbrc/home/out/r/.align/alignment"})
        self.assertEqual(a["folder"], "/u@bvbrc/home/out/r/.align")
        self.assertEqual((t["id"], t["state"], t["elapsed"]), ("tree", "PENDING", ""))
        self.assertEqual(gb.cancel(self.server, job, TOKEN)["state"], "CANCELLED")
        only = gb.log(self.server, job, TOKEN, step="align")
        self.assertIn("boom", only)
        self.assertNotIn("=== tree", only)


if __name__ == "__main__":
    unittest.main()
