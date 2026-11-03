"""Prototype HTTP API for the ModularPipeline web form (BV-BRC-Web p3/widget/app/ModularPipeline.js).

    bin/modpipe serve [--host 127.0.0.1] [--port 8765] [--origin URL ...]
                      [--tls-cert C --tls-key K | --self-signed]

The production app service does not know the ModularPipeline app yet, so this server stands in for it: it lists
templates, validates pipelines, and submits jobs to Slurm by running App-ModularPipeline exactly like
tests/app/run_app.sbatch does. Jobs run with the BV-BRC token sent by the browser (Authorization header) and
write results to that user's workspace.

Endpoints (JSON):
  GET  /api/health
  GET  /api/templates                 curated templates (+ per-input source options for the form)
  GET  /api/modules                   module catalog
  GET  /api/catalog                   types + converters + modules (ports, params) for the graph editor
  GET  /api/templates/<name>          one template as an editable pipeline (template.optional/links -> ui)
  GET  /api/source_options?type=&collection=1   data sources a pipeline input of that type can use
  GET  /api/databases?type=<type>     registry entries usable for a database parameter
  POST /api/instantiate   {template, inputs, template_params}           -> {ok, errors, warnings, pipeline, resources}
  POST /api/validate      {pipeline}                                     -> same
  POST /api/submit        {pipeline | template+inputs+template_params, output_path, output_file}  (auth) -> {job}
  GET  /api/jobs                      (auth) this user's jobs with Slurm state
  GET  /api/jobs/<id>/log             (auth) tail of the job log
Prototype limits: the token is trusted as given (the workspace and data API enforce access); no rate limiting.
"""
import datetime
import hashlib
import json
import os
import re
import subprocess
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .pipeline import Validator, auto_convert
from .registry import DatabaseRegistry, ModuleRegistry
from .templates import TemplateError, instantiate
from .types import TypeSystem
from .util import read_json, read_yaml, repo_path

STATE_DIR = os.environ.get("MODPIPE_UI_STATE", os.path.expanduser("~/.modpipe-ui"))
_lock = threading.Lock()
TOKEN_USER = re.compile(r"(?:^|\|)un=([^|]+)")
JOB_ID = re.compile(r"^[a-f0-9]{12}$")


class ApiError(Exception):
    def __init__(self, status, msg, extra=None):
        super().__init__(msg)
        self.status, self.msg, self.extra = status, msg, extra or {}


# ------------------------------------------------------------------ catalog helpers

class Catalog:
    def __init__(self):
        self.ts = TypeSystem()
        self.dbs = DatabaseRegistry()
        self.mods = ModuleRegistry(self.ts, self.dbs)
        self.wst = read_yaml(repo_path("types", "wstypes.yaml"))

    def wstypes_for(self, tid):
        """Workspace types whose candidates are compatible with type `tid` (for the workspace file chooser)."""
        out = []
        for w, d in self.wst["accept"].items():
            for c in d.get("candidates") or []:
                if self.ts.is_a(c, tid) or self.ts.is_a(tid, c):
                    out.append(w)
                    break
        return sorted(set(out))

    def source_options(self, tid, collection):
        ts = self.ts
        opts = []
        if ts.is_a(tid, "reads.short.paired"):
            opts += [{"kind": "paired_end_libs", "label": "Paired-end reads from workspace", "wstypes": ["reads"]},
                     {"kind": "srr_ids", "label": "SRA run accessions"}]
        elif ts.is_a(tid, "reads"):
            opts += [{"kind": "single_end_libs", "label": "Reads file(s) from workspace", "wstypes": ["reads"]},
                     {"kind": "srr_ids", "label": "SRA run accessions"}]
        else:
            ws = self.wstypes_for(tid)
            if ws:
                opts.append({"kind": "wsids" if collection else "wsid", "label": "Workspace file" + ("s" if collection else ""),
                             "wstypes": ws})
            if ts.is_a(tid, "sequences.dna"):
                opts.append({"kind": "genome_ids", "label": "BV-BRC genome ID" + ("s" if collection else "")})
                if collection:
                    opts.append({"kind": "genome_group", "label": "Genome group", "wstypes": ["genome_group"]})
            if ts.is_a(tid, "sequences"):
                opts += [{"kind": "feature_group", "label": "Feature group", "wstypes": ["feature_group"]},
                         {"kind": "feature_ids", "label": "BV-BRC feature IDs (fig|...)"}]
                if not collection:
                    opts.append({"kind": "fasta_data", "label": "Paste FASTA"})
            files = [{"value": f"{e['id']}:{k}", "label": f"{e.get('description', e['id'])} [{k}]"}
                     for e in self.dbs.dbs.values() for k in (e.get("files") or {})
                     if k == "reference" and ts.is_a(tid, "sequences.dna")]
            if files and not collection:
                opts.append({"kind": "database_file", "label": "Bundled reference", "choices": files})
        return opts

    def param_spec(self, mid, pid):
        m = self.mods.get(mid)
        spec = dict(m.params.get(pid, {})) if m else {}
        if spec.get("type") == "database":
            spec["choices"] = [{"value": e["id"], "label": e.get("description") or e["id"], "status": e.get("status")}
                               for e in self.dbs.of_type(self.ts, spec["db_type"]) if e.get("status") != "missing"]
        return spec

    def templates(self):
        rows = []
        for f in sorted(os.listdir(repo_path("pipelines"))):
            if not f.endswith(".json"):
                continue
            p = read_json(repo_path("pipelines", f))
            t = p.get("template") or {}
            params = []
            for key in t.get("expose") or []:
                step, _, pid = key.split(".", 2)
                spec = self.param_spec(p["steps"][step]["module"], pid)
                spec.update({"key": key, "step": step, "module": p["steps"][step]["module"]})
                params.append(spec)
            rows.append({
                "template": f[:-5], "label": t.get("label") or p.get("name"), "category": t.get("category"),
                "name": p.get("name"), "description": p.get("description"),
                "inputs": [{"name": k, "type": v["type"], "collection": bool(v.get("collection")),
                            "type_description": self.ts.get(v["type"]).get("description"),
                            "default_source": v.get("source") if "database_file" in (v.get("source") or {}) else None,
                            "source_options": self.source_options(v["type"], bool(v.get("collection")))}
                           for k, v in (p.get("inputs") or {}).items()],
                "params": params,
                "optional_steps": [{"step": k, "label": v.get("label", k), "default": v.get("default", True),
                                    "module": p["steps"][k]["module"]} for k, v in (t.get("optional") or {}).items()],
                "outputs": sorted(p.get("outputs") or {}),
                "steps": [{"id": k, "module": v["module"]} for k, v in p["steps"].items()]})
        return rows

    def catalog(self):
        """Everything the graph editor needs for instant (client-side) connection checks and the palette."""
        if getattr(self, "_catalog", None) is None:
            ts = self.ts
            types = {t: {k: d.get(k) for k in ("abstract", "kind", "description", "registry_only") if d.get(k) is not None}
                     for t, d in ts.types.items()}
            mods = {}
            for m in sorted(self.mods.modules.values(), key=lambda m: m.id):
                d = m.d
                mods[m.id] = {
                    "id": m.id, "version": m.version, "label": d.get("label"), "description": d.get("description"),
                    "category": d.get("category"), "tool": d.get("tool"), "resources": d.get("resources"),
                    "inputs": [{k: p.get(k) for k in ("id", "type", "required", "cardinality", "description", "requires")
                                if p.get(k) is not None} for p in m.inputs.values()],
                    "outputs": [{k: p.get(k) for k in ("id", "type", "type_from", "description", "attributes", "when")
                                 if p.get(k) is not None} for p in m.outputs.values()],
                    "params": [self.param_spec(m.id, pid) for pid in m.params]}
            cats = {}
            for m in mods.values():
                cats.setdefault(m["category"] or "other", []).append(m["id"])
            body = {"types": types, "attributes": ts.attributes, "converters": ts.converters, "modules": mods,
                    "categories": cats}
            body["version"] = hashlib.sha1(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()[:12]
            self._catalog = body
        return self._catalog

    def template_pipeline(self, name):
        """A curated template as an editable pipeline: example sources dropped (except bundled references),
        template.optional/links moved to the editor's ui key, source options per input."""
        if not re.match(r"^[A-Za-z0-9_]+$", name) or not os.path.isfile(repo_path("pipelines", f"{name}.json")):
            raise ApiError(404, f"unknown template {name!r}")
        p = read_json(repo_path("pipelines", f"{name}.json"))
        t = p.pop("template", None) or {}
        for d in (p.get("inputs") or {}).values():
            src = d.get("source") or {}
            d["source"] = {"database_file": src["database_file"]} if "database_file" in src else {}
        ui = {}
        if t.get("optional"):
            ui["optional"] = t["optional"]
            off = [k for k, v in t["optional"].items() if not v.get("default", True)]
            if off:
                ui["disabled"] = off
        if t.get("links"):
            ui["links"] = t["links"]
        if ui:
            p["ui"] = ui
        return {"template": name, "label": t.get("label") or p.get("name"), "pipeline": p,
                "source_options": {k: self.source_options(v["type"], bool(v.get("collection")))
                                   for k, v in (p.get("inputs") or {}).items()}}

    def check(self, p):
        p2, iss, plan = auto_convert(Validator(self.ts, self.mods, self.dbs), p)
        r = plan.get("resources") or {}
        return {"ok": iss.ok, "errors": iss.errors, "warnings": iss.warnings, "issues": iss.items, "pipeline": p2,
                "resources": {k: r.get(k) for k in ("cpu", "memory_gb", "runtime", "runtime_s", "partition")},
                "steps": {sid: {"module": st["module"], "scatter": st["scatter"], "scatter_size": st.get("scatter_size"),
                                "outputs": st["outputs"], "output_types": st.get("output_types"),
                                "auto": bool((p2.get("steps") or {}).get(sid, {}).get("auto"))}
                          for sid, st in plan.get("steps", {}).items()}}


# ------------------------------------------------------------------ jobs

def _jobs_file():
    os.makedirs(STATE_DIR, mode=0o700, exist_ok=True)
    return os.path.join(STATE_DIR, "jobs.json")


def _load_jobs():
    f = _jobs_file()
    return read_json(f) if os.path.exists(f) else []


def _save_jobs(jobs):
    f = _jobs_file()
    tmp = f + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(jobs, fh, indent=1)
    os.replace(tmp, f)


def _slurm_state(ids):
    if not ids:
        return {}
    try:
        out = subprocess.run(["sacct", "-n", "-X", "-P", "-j", ",".join(ids), "--format=JobID,State,Elapsed,ExitCode,NodeList"],
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=30).stdout.decode()
    except Exception:
        return {}
    res = {}
    for line in out.splitlines():
        parts = line.split("|")
        if len(parts) >= 5:
            res[parts[0]] = {"state": parts[1].split()[0], "elapsed": parts[2], "exit_code": parts[3], "node": parts[4]}
    return res


def _sbatch_args(resources):
    cpu = max(1, min(int(resources.get("cpu") or 4), 32))
    mem = max(4, min(int((resources.get("memory_gb") or 8) + 0.999), 256))
    secs = int((resources.get("runtime_s") or 3600) * 1.2) + 1800
    hours = max(1, min(48, -(-secs // 3600)))
    args = ["--cpus-per-task", str(cpu), "--mem", f"{mem}G", "--time", f"{hours}:00:00"]
    if resources.get("partition"):
        args += ["--partition", resources["partition"]]
    return args


def submit(cat, body, token, user):
    if body.get("pipeline") and body.get("template"):
        raise ApiError(400, "give either pipeline or template, not both")
    for k in ("output_path", "output_file"):
        if not body.get(k) or not isinstance(body[k], str):
            raise ApiError(400, f"{k} is required")
    if not re.match(r"^[A-Za-z0-9 _.()+-]{1,100}$", body["output_file"]):
        raise ApiError(400, "output_file may only contain letters, digits, spaces and _ . ( ) + -")
    if not body["output_path"].startswith("/") or ".." in body["output_path"]:
        raise ApiError(400, "output_path must be an absolute workspace path")
    if body.get("template"):
        try:
            p = instantiate(body["template"], body.get("inputs"), body.get("template_params"))
        except TemplateError as e:
            raise ApiError(400, str(e))
    else:
        p = body.get("pipeline")
        if not isinstance(p, dict):
            raise ApiError(400, "pipeline must be an object")
    res = cat.check(p)
    if not res["ok"]:
        raise ApiError(400, "pipeline is invalid", {"errors": res["errors"], "warnings": res["warnings"]})

    jid = uuid.uuid4().hex[:12]
    jdir = os.path.join(STATE_DIR, "jobs", jid)
    os.makedirs(jdir, mode=0o700)
    params = {"pipeline": res["pipeline"], "output_path": body["output_path"], "output_file": body["output_file"],
              "keep_intermediates": bool(body.get("keep_intermediates"))}
    pfile = os.path.join(jdir, "params.json")
    with open(pfile, "w") as f:
        json.dump(params, f, indent=1)
    tfile = os.path.join(jdir, "token")
    fd = os.open(tfile, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(token)
    log = os.path.join(jdir, "slurm.out")
    cmd = (["sbatch", "--parsable", "--job-name", f"modpipe-ui-{jid}", "--output", log, "--chdir", repo_path()]
           + _sbatch_args(res["resources"]) + ["--export", f"ALL,MODPIPE_TOKEN_FILE={tfile}",
                                               repo_path("tests", "app", "run_app.sbatch"), pfile])
    p_ = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    if p_.returncode != 0:
        raise ApiError(502, "sbatch failed: " + p_.stderr.decode(errors="replace")[-300:])
    slurm_id = p_.stdout.decode().strip().split(";")[0]
    job = {"id": jid, "slurm_id": slurm_id, "user": user, "name": p.get("name"), "template": body.get("template"),
           "output_path": body["output_path"], "output_file": body["output_file"],
           "result_folder": f"{body['output_path'].rstrip('/')}/.{body['output_file']}",
           "submitted": datetime.datetime.now().isoformat(timespec="seconds"),
           "resources": res["resources"], "warnings": res["warnings"]}
    with _lock:
        jobs = _load_jobs()
        jobs.append(job)
        _save_jobs(jobs)
    return job


def list_jobs(user):
    with _lock:
        jobs = [j for j in _load_jobs() if j["user"] == user]
    st = _slurm_state([j["slurm_id"] for j in jobs])
    for j in jobs:
        j.update(st.get(j["slurm_id"], {"state": "UNKNOWN"}))
        log = os.path.join(STATE_DIR, "jobs", j["id"], "slurm.out")
        if j.get("state") == "COMPLETED" and os.path.exists(log):
            with open(log, errors="replace") as f:
                txt = f.read()
            j["pipeline_status"] = "failed" if ("RUN FAILED" in txt or "Exception raised while executing" in txt) else "ok"
    return sorted(jobs, key=lambda j: j["submitted"], reverse=True)


def job_log(user, jid):
    if not JOB_ID.match(jid):
        raise ApiError(404, "no such job")
    with _lock:
        j = next((j for j in _load_jobs() if j["id"] == jid and j["user"] == user), None)
    if not j:
        raise ApiError(404, "no such job")
    log = os.path.join(STATE_DIR, "jobs", jid, "slurm.out")
    if not os.path.exists(log):
        return {"id": jid, "log": "(job has not started yet)"}
    with open(log, errors="replace") as f:
        lines = [l for l in f.read().splitlines() if not l.startswith("INFO:")]
    return {"id": jid, "log": "\n".join(lines[-200:])}


# ------------------------------------------------------------------ HTTP

def make_handler(cat, origins):
    class H(BaseHTTPRequestHandler):
        server_version = "modpipe-api/0.1"

        def log_message(self, fmt, *args):      # no tokens in logs: only method + path
            print(f"[modpipe-api] {self.command} {urlparse(self.path).path} -> {args[1] if len(args) > 1 else ''}", flush=True)

        def _cors(self):
            o = self.headers.get("Origin")
            if o and (o in origins or "*" in origins):
                self.send_header("Access-Control-Allow-Origin", o)
                self.send_header("Vary", "Origin")
                self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-Requested-With")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

        def _send(self, status, obj):
            data = json.dumps(obj, default=str).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self._cors()
            self.end_headers()
            self.wfile.write(data)

        def _auth(self):
            tok = (self.headers.get("Authorization") or "").strip()
            if tok.lower().startswith("oauth "):
                tok = tok[6:]
            m = TOKEN_USER.search(tok)
            if not tok or not m:
                raise ApiError(401, "sign in to BV-BRC first (no valid token)")
            return tok, m.group(1)

        def _body(self):
            n = int(self.headers.get("Content-Length") or 0)
            if n > 5_000_000:
                raise ApiError(413, "request too large")
            try:
                return json.loads(self.rfile.read(n) or b"{}")
            except json.JSONDecodeError as e:
                raise ApiError(400, f"bad JSON: {e}")

        def do_OPTIONS(self):
            self.send_response(204)
            self._cors()
            self.end_headers()

        def do_GET(self):
            self._route("GET")

        def do_POST(self):
            self._route("POST")

        def _route(self, method):
            u = urlparse(self.path)
            path, q = u.path.rstrip("/"), parse_qs(u.query)
            try:
                if method == "GET" and path == "/api/health":
                    return self._send(200, {"ok": True, "modules": len(cat.mods.modules)})
                if method == "GET" and path == "/api/templates":
                    return self._send(200, cat.templates())
                if method == "GET" and path == "/api/catalog":
                    return self._send(200, cat.catalog())
                m = re.match(r"^/api/templates/([^/]+)$", path)
                if method == "GET" and m:
                    return self._send(200, cat.template_pipeline(m.group(1)))
                if method == "GET" and path == "/api/source_options":
                    t = (q.get("type") or [""])[0]
                    if t not in cat.ts:
                        raise ApiError(400, f"unknown type {t!r}")
                    coll = (q.get("collection") or ["0"])[0] in ("1", "true")
                    return self._send(200, cat.source_options(t, coll))
                if method == "GET" and path == "/api/modules":
                    return self._send(200, [m.summary() for m in cat.mods.modules.values()])
                if method == "GET" and path == "/api/databases":
                    t = (q.get("type") or [""])[0]
                    rows = [e for e in cat.dbs.dbs.values() if not t or cat.ts.is_a(e["type"], t)]
                    return self._send(200, rows)
                if method == "POST" and path == "/api/instantiate":
                    b = self._body()
                    try:
                        p = instantiate(b.get("template", ""), b.get("inputs"), b.get("template_params"))
                    except TemplateError as e:
                        return self._send(200, {"ok": False, "errors": [str(e)], "warnings": []})
                    return self._send(200, cat.check(p))
                if method == "POST" and path == "/api/validate":
                    b = self._body()
                    if not isinstance(b.get("pipeline"), dict):
                        raise ApiError(400, "body must be {pipeline: {...}}")
                    return self._send(200, cat.check(b["pipeline"]))
                if method == "POST" and path == "/api/submit":
                    tok, user = self._auth()
                    return self._send(200, {"job": submit(cat, self._body(), tok, user)})
                if method == "GET" and path == "/api/jobs":
                    _, user = self._auth()
                    return self._send(200, list_jobs(user))
                m = re.match(r"^/api/jobs/([^/]+)/log$", path)
                if method == "GET" and m:
                    _, user = self._auth()
                    return self._send(200, job_log(user, m.group(1)))
                raise ApiError(404, f"no route {method} {path}")
            except ApiError as e:
                self._send(e.status, {"ok": False, "error": e.msg, **e.extra})
            except Exception as e:            # keep the server alive; report without internals
                self._send(500, {"ok": False, "error": f"internal error: {type(e).__name__}"})
                raise
    return H


def self_signed_cert(hostname):
    """Create (once) a self-signed certificate for `hostname` under the state dir; returns (cert, key)."""
    import subprocess
    d = os.path.join(STATE_DIR, "tls")
    os.makedirs(d, mode=0o700, exist_ok=True)
    cert, key = os.path.join(d, f"{hostname}.crt"), os.path.join(d, f"{hostname}.key")
    if not (os.path.exists(cert) and os.path.exists(key)):
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "365",
                        "-keyout", key, "-out", cert, "-subj", f"/CN={hostname}",
                        "-addext", f"subjectAltName=DNS:{hostname},DNS:localhost,IP:127.0.0.1"],
                       check=True, capture_output=True)
        os.chmod(key, 0o600)
    return cert, key


DEFAULT_ORIGINS = ("https://dev-5.bv-brc.org", "http://localhost:3000")


def serve(host="127.0.0.1", port=8765, origins=DEFAULT_ORIGINS, cert=None, key=None):
    cat = Catalog()
    httpd = ThreadingHTTPServer((host, port), make_handler(cat, set(origins)))
    scheme = "http"
    if cert:
        import ssl
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain(cert, key)
        httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
        scheme = "https"
    print(f"[modpipe-api] serving on {scheme}://{host}:{port}  (CORS origins: {', '.join(origins)}; state: {STATE_DIR})", flush=True)
    if cert:
        print(f"[modpipe-api] TLS certificate: {cert}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
