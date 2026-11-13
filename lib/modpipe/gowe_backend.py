"""GoWe backend for the modpipe API (bin/modpipe serve --backend gowe): submit a pipeline as a GoWe workflow.

submit: modpipe compile -> `gowe bundle` -> POST /api/v1/workflows/ -> POST /api/v1/submissions/, all with the
user's own BV-BRC token (Authorization: Bearer). GoWe keeps the token for the submission (and injects it only into
blessed tools); this server never writes it to disk. Each step is one ModularStep job; results land in
<output_path>/<run_name>/.<step>/<port>/ (one folder per run).

status / log: GET the submission, its tasks and their logs, again as the user (GoWe only shows a user their own
submissions).
"""
import datetime
import json
import os
import re
import subprocess
import urllib.error
import urllib.request

from .compile import CompileError, compile_pipeline, slug, write

GOWE_DIR = os.environ.get("GOWE_DIR") or os.path.expanduser("~/bvbrc-dev/Copilot/Agents/GoWe")
WORKSPACE_URL = os.environ.get("MODPIPE_WORKSPACE_URL") or "https://p3.theseed.org/services/Workspace"
STATE_MAP = {"PENDING": "PENDING", "QUEUED": "PENDING", "SCHEDULED": "PENDING", "RUNNING": "RUNNING",
             "COMPLETED": "COMPLETED", "FAILED": "FAILED", "CANCELLED": "CANCELLED", "CANCELED": "CANCELLED"}


class GoweError(Exception):
    def __init__(self, status, msg, extra=None):
        super().__init__(msg)
        self.status, self.msg, self.extra = status, msg, extra or {}


def run_name_for(output_file):
    """A job name usable as the step job-name prefix (letters, digits, . _ -)."""
    s = re.sub(r"[^A-Za-z0-9_.-]+", "_", output_file).strip("_.-")[:56]
    return s if s and s[0].isalnum() else f"run_{s}"[:56]


def _call(server, method, path, token, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(server.rstrip("/") + path, data=data, method=method,
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r).get("data")
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode(errors="replace")).get("error") or {}
        except (ValueError, AttributeError):
            err = {}
        msg = err.get("message") if isinstance(err, dict) else str(err)
        details = err.get("details") if isinstance(err, dict) else None
        if e.code == 401:
            raise GoweError(401, "GoWe did not accept your BV-BRC token (sign in again)")
        raise GoweError(502, f"GoWe {method} {path.split('?')[0]}: HTTP {e.code}: {msg or e.reason}",
                        {"gowe_details": details} if details else None)
    except (urllib.error.URLError, OSError) as e:
        raise GoweError(502, f"GoWe server {server} unreachable: {getattr(e, 'reason', e)}")


def ws_exists(token, path):
    """True if the workspace path exists (as the user); None if the Workspace could not be asked."""
    body = json.dumps({"method": "Workspace.get", "version": "1.1", "id": "1",
                       "params": [{"objects": [path], "metadata_only": 1}]}).encode()
    req = urllib.request.Request(WORKSPACE_URL, data=body, headers={"Authorization": token,
                                                                    "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.load(r).get("result") or [[]]
        return bool(res and res[0])
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read().decode(errors="replace")).get("error", {}).get("message", "")
        except (ValueError, AttributeError):
            msg = ""
        return False if "not found" in msg.lower() or "does not exist" in msg.lower() else None
    except (urllib.error.URLError, OSError, ValueError):
        return None


def submit(server, cat, p, output_path, output_file, token, jdir):
    """Compile, register and submit; returns the job fields to record."""
    run_name = run_name_for(output_file)
    try:
        wf, job, info = compile_pipeline(p, cat.ts, cat.mods, cat.dbs)
    except CompileError as e:
        raise GoweError(400, "pipeline cannot run through GoWe", {"errors": e.errors, "warnings": e.warnings})
    run_folder = f"{output_path.rstrip('/')}/{run_name}"
    # steps would write into an existing run's folder (.<step>/ overwritten or mixed): refuse
    if ws_exists(token, run_folder):
        raise GoweError(409, f"{run_folder} already exists; choose another run name")
    job["output_path"] = run_folder
    name = slug(p.get("name"))
    wf_path = write(jdir, wf, job, info["tools_dir"], name)
    b = subprocess.run([os.path.join(GOWE_DIR, "bin", "gowe"), "bundle", wf_path], capture_output=True, text=True,
                       timeout=120)
    if b.returncode != 0:
        raise GoweError(500, "gowe bundle failed: " + (b.stderr or b.stdout).strip()[-300:])
    wfr = _call(server, "POST", "/api/v1/workflows/", token, {"name": name, "cwl": b.stdout})
    sub = _call(server, "POST", "/api/v1/submissions/", token, {"workflow_id": wfr["id"], "inputs": job})
    return {"backend": "gowe", "gowe_submission": sub["id"], "gowe_workflow": wfr["id"], "workflow_name": name,
            "run_name": run_name, "steps": info["order"], "release_tools": info["tools_dir"],
            # the run folder: one result folder per step, .<step>/
            "result_folder": run_folder, "warnings": info["warnings"]}


def _parse_ts(s):
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(re.sub(r"(\.\d{6})\d+", r"\1", s).replace("Z", "+00:00"))
    except ValueError:
        return None


def status(server, job, token):
    """{state, elapsed, steps_done, steps_total, outputs} for a recorded GoWe job (state UNKNOWN on errors)."""
    try:
        d = _call(server, "GET", f"/api/v1/submissions/{job['gowe_submission']}", token, timeout=20)
    except GoweError as e:
        return {"state": "UNKNOWN", "status_error": e.msg}
    ts = d.get("task_summary") or {}
    start, end = _parse_ts(d.get("created_at")), _parse_ts(d.get("completed_at"))
    el = ""
    if start:
        secs = int(((end or datetime.datetime.now(datetime.timezone.utc)) - start).total_seconds())
        el = f"{secs // 3600:d}:{secs % 3600 // 60:02d}:{secs % 60:02d}"
    total = ts.get("total") or len(job.get("steps") or [])
    return {"state": STATE_MAP.get(str(d.get("state", "")).upper(), d.get("state") or "UNKNOWN"), "elapsed": el,
            "steps_done": ts.get("success", 0), "steps_failed": ts.get("failed", 0),
            "steps_total": max(total, len(job.get("steps") or [])),
            "outputs": {k: v for k, v in (d.get("outputs") or {}).items() if isinstance(v, str)}}


def _tasks(server, job, token):
    tasks = _call(server, "GET", f"/api/v1/submissions/{job['gowe_submission']}/tasks/", token, timeout=30) or []
    if isinstance(tasks, dict):
        tasks = tasks.get("tasks") or []
    order = {s: i for i, s in enumerate(job.get("steps") or [])}
    tasks.sort(key=lambda t: (order.get(t.get("step_id"), 99), t.get("created_at") or ""))
    return tasks


def _elapsed(start, end):
    a, b = _parse_ts(start), _parse_ts(end)
    if not a:
        return ""
    secs = int(((b or datetime.datetime.now(datetime.timezone.utc)) - a).total_seconds())
    return f"{secs // 3600:d}:{secs % 3600 // 60:02d}:{secs % 60:02d}"


def detail(server, job, token):
    """status() plus one entry per pipeline step: {id, module, state, started, completed, elapsed, outputs, task}.
    Steps without a task yet are PENDING; the last task of a step (retries) wins."""
    st = status(server, job, token)
    by_step = {}
    try:
        for t in _tasks(server, job, token):
            by_step[t.get("step_id")] = t
    except GoweError as e:
        st["status_error"] = e.msg
    mods = {sid: (s or {}).get("module") for sid, s in ((job.get("pipeline") or {}).get("steps") or {}).items()}
    steps = []
    for sid in job.get("steps") or []:
        t = by_step.get(sid) or {}
        state = str(t.get("state") or "PENDING").upper()
        steps.append({"id": sid, "module": mods.get(sid), "state": state, "task": t.get("id"),
                      "started": t.get("started_at"), "completed": t.get("completed_at"),
                      "elapsed": _elapsed(t.get("started_at"), t.get("completed_at")) if t.get("started_at") else "",
                      "folder": f"{job.get('result_folder', '').rstrip('/')}/.{sid}",
                      "outputs": {k: v for k, v in (t.get("outputs") or {}).items() if isinstance(v, str)}})
    st["step_detail"] = steps
    return st


def cancel(server, job, token):
    return _call(server, "PUT", f"/api/v1/submissions/{job['gowe_submission']}/cancel", token, {}, timeout=30)


def log(server, job, token, lines_per_step=120, step=None):
    """Per-step log tails (stdout + stderr) in workflow order; only `step` if given."""
    tasks = _tasks(server, job, token)
    if step:
        tasks = [t for t in tasks if t.get("step_id") == step]
    out = []
    for t in tasks:
        out.append(f"=== {t.get('step_id')}  {t.get('state')}  ({t.get('id')})")
        if str(t.get("state")).upper() in ("PENDING", "QUEUED", "SCHEDULED"):
            out.append("(not started)")
            continue
        try:
            lg = _call(server, "GET", f"/api/v1/submissions/{job['gowe_submission']}/tasks/{t['id']}/logs", token,
                       timeout=30) or {}
        except GoweError as e:
            out.append(f"(log unavailable: {e.msg})")
            continue
        text = "\n".join(x for x in ((lg.get("stdout") or "").rstrip(), (lg.get("stderr") or "").rstrip()) if x)
        lines = [l for l in text.splitlines() if not l.startswith("INFO:")]
        if len(lines) > lines_per_step:
            out.append(f"... ({len(lines) - lines_per_step} earlier lines)")
        out.extend(lines[-lines_per_step:])
        if lg.get("exit_code") not in (None, 0):
            out.append(f"[exit code {lg.get('exit_code')}]")
    return "\n".join(out) or "(no tasks yet)"
