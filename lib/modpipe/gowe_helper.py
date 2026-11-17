"""Helper steps that compile inserts around service modules (`modpipe gowe-helper <cmd> job.json`, on a GoWe worker).

    value-file   {value}          -> {path}       an upstream port/value folder -> the workspace path of its one file
    wait-genome  {gto, timeout}   -> {genome_id}  wait until BV-BRC has indexed an annotated genome, return its id

Both read the CWL job (job.json), use the submitter's token from the environment (GoWe injects BVBRC_TOKEN /
KB_AUTH_TOKEN into blessed tools; never printed) and write cwl.output.json. Standard library only (they run in the
production container's python).
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

WORKSPACE_URL = os.environ.get("MODPIPE_WORKSPACE_URL") or "https://p3.theseed.org/services/Workspace"
DATA_API_URL = os.environ.get("MODPIPE_DATA_API_URL") or "https://www.bv-brc.org/api"


class HelperError(Exception):
    pass


def _token():
    for k in ("P3_AUTH_TOKEN", "KB_AUTH_TOKEN", "BVBRC_TOKEN"):
        if os.environ.get(k):
            return os.environ[k]
    raise HelperError("no BV-BRC token in the environment (BVBRC_TOKEN / KB_AUTH_TOKEN)")


def ws_call(method, params, token):
    body = json.dumps({"method": "Workspace." + method, "params": [params], "version": "1.1", "id": "1"}).encode()
    req = urllib.request.Request(WORKSPACE_URL, data=body, headers={"Authorization": token,
                                                                    "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)["result"]
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read().decode(errors="replace")).get("error", {}).get("message", "")
        except (ValueError, AttributeError):
            msg = ""
        raise HelperError("Workspace.%s: HTTP %s %s" % (method, e.code, msg.strip()[:300]))


def ws_meta(path, token):
    """(type, user metadata, auto metadata) of a workspace object, or None if it does not exist."""
    try:
        res = ws_call("get", {"objects": [path], "metadata_only": 1}, token)
    except HelperError as e:
        if "not found" in str(e).lower() or "does not exist" in str(e).lower():
            return None
        raise
    m = res[0][0][0] if res and res[0] else None
    if not m:
        return None
    return m[1], (m[7] or {}), (m[8] or {})


def ws_children(path, token):
    res = ws_call("ls", {"paths": [path]}, token)
    return [(r[2] + r[0], r[1]) for r in (res[0] or {}).get(path, [])]


def _plain(v):
    """A CWL value (string, File/Directory object, one-item list) -> workspace path string."""
    if isinstance(v, list):
        if len(v) != 1:
            raise HelperError("expected one value, got %d" % len(v))
        v = v[0]
    if isinstance(v, dict):
        v = v.get("location") or v.get("path") or ""
    if not isinstance(v, str) or not v:
        raise HelperError("expected a workspace path, got %r" % (v,))
    for scheme in ("ws://", "file://"):
        if v.startswith(scheme):
            v = v[len(scheme):]
    return v.rstrip("/")


def value_file(value, token, depth=0):
    """Workspace path of the one file behind a port folder, a value folder or a file."""
    path = _plain(value)
    meta = ws_meta(path, token)
    if meta is None:
        raise HelperError("%s does not exist" % path)
    wstype, um, _ = meta
    if wstype != "folder":
        return path
    files = um.get("modpipe_files")
    if files:
        files = json.loads(files) if isinstance(files, str) else files
        if len(files) != 1:
            raise HelperError("%s holds a %s with parts %s; a service step takes one file"
                              % (path, um.get("modpipe_type"), sorted(files)))
        return path + "/" + list(files.values())[0]
    kids = ws_children(path, token)
    if len(kids) == 1 and depth < 3:
        return value_file(kids[0][0], token, depth + 1)        # a port folder with one sample folder
    raise HelperError("%s is a folder with %d items (%s); a service step takes one genome, not a sample collection"
                      % (path, len(kids), ", ".join(k[0].rsplit("/", 1)[-1] for k in kids[:5])))


def _data_api(query, token, count=False):
    headers = {"Authorization": token, "Accept": "application/json", "User-Agent": "modpipe-gowe-helper"}
    if count:
        headers["X-Range"] = "items=0-0"
    req = urllib.request.Request(DATA_API_URL.rstrip("/") + "/" + query, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        rows = json.load(r)
        if count:
            cr = r.headers.get("Content-Range") or ""
            return int(cr.rsplit("/", 1)[-1]) if "/" in cr else len(rows)
        return rows


def genome_indexed(genome_id, token):
    """(done, detail): the genome record is in the data API and its features are in (count >= the record's CDS)."""
    gid = urllib.parse.quote(genome_id, safe="")
    rows = _data_api("genome/?eq(genome_id,%s)&select(genome_id,cds,patric_cds)" % gid, token)
    if not rows:
        return False, "genome record not indexed yet"
    want = int(rows[0].get("patric_cds") or rows[0].get("cds") or 0)
    have = _data_api("genome_feature/?eq(genome_id,%s)&limit(1)&select(feature_id)" % gid, token, count=True)
    if have < max(want, 1):
        return False, "%d of >= %d features indexed" % (have, want)
    return True, "%d features indexed" % have


def wait_genome(gto, token, timeout=7200, interval=30, sleep=time.sleep, now=time.time):
    path = _plain(gto)
    meta = ws_meta(path, token)
    if meta is None:
        raise HelperError("%s does not exist" % path)
    gid = meta[2].get("genome_id")
    if not gid:
        raise HelperError("%s has no genome_id in its workspace metadata (not an annotated genome?)" % path)
    start = now()
    while True:
        try:
            done, detail = genome_indexed(gid, token)
        except (urllib.error.URLError, OSError, ValueError) as e:
            done, detail = False, "data API error: %s" % (getattr(e, "reason", None) or e)
        print("wait-genome: %s: %s" % (gid, detail), file=sys.stderr, flush=True)
        if done:
            return gid
        if now() - start >= timeout:
            raise HelperError("genome %s not indexed after %ds (%s)" % (gid, timeout, detail))
        sleep(interval)


def main(cmd, job_path, workdir="."):
    with open(job_path) as f:
        job = json.load(f)
    try:
        token = _token()
        if cmd == "value-file":
            out = {"path": value_file(job.get("value"), token)}
        elif cmd == "wait-genome":
            out = {"genome_id": wait_genome(job.get("gto"), token, timeout=int(job.get("timeout") or 7200))}
        else:
            raise HelperError("unknown helper %r (value-file, wait-genome)" % cmd)
    except HelperError as e:
        print("gowe-helper %s: %s" % (cmd, e), file=sys.stderr)
        return 1
    print("gowe-helper %s: %s" % (cmd, json.dumps(out)), file=sys.stderr)
    with open(os.path.join(workdir, "cwl.output.json"), "w") as f:
        json.dump(out, f)
    return 0
