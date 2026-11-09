#!/usr/bin/env python3
"""Register the generated modpipe CWL tools (modpipe export-cwl) on a GoWe server as workflows `modpipe-<module>`.

    deploy/gowe/register_tools.py [--server URL] [--dir cwl/tools] [module ...]

The token is read from MODPIPE_TOKEN_FILE (default ~/.patric_token), never from the command line. Registration is
append-only on the server: unchanged content is deduplicated, changed content becomes a new version under the
same name (submit by wf_ id to pin one). Blessing (token injection) is a separate admin step (release.sh).

Each tool is uploaded packed (`gowe bundle`, as `gowe register` does): a bare tool is wrapped by the server into a
one-step workflow with the tool's hints copied onto the step, and a step-level DockerRequirement on a
token-requesting tool is refused at submit (TOKEN_TOOL_OVERRIDE_REFUSED). The packed wrapper leaves the step bare;
the tool, and so its hash and blessing, are the same.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("modules", nargs="*")
ap.add_argument("--server", default=os.environ.get("GOWE_SERVER", "http://localhost:12007"))
ap.add_argument("--dir", default=os.path.join(os.path.dirname(__file__), "..", "..", "cwl", "tools"))
ap.add_argument("--gowe", default=os.path.join(os.environ.get("GOWE_DIR", os.path.expanduser("~/bvbrc-dev/Copilot/Agents/GoWe")),
                                              "bin", "gowe"), help="gowe CLI (for `gowe bundle`)")
ap.add_argument("--json-out", help="write {module: {name, id, deduplicated}} here")
a = ap.parse_args()
with open(os.path.expanduser(os.environ.get("MODPIPE_TOKEN_FILE", "~/.patric_token"))) as f:
    token = f.read().strip()
names = a.modules or sorted(f[:-4] for f in os.listdir(a.dir) if f.endswith(".cwl"))
failed = 0
registered = {}
for mid in names:
    b = subprocess.run([a.gowe, "bundle", os.path.join(a.dir, f"{mid}.cwl")], capture_output=True, text=True)
    if b.returncode != 0:
        failed += 1
        print(f"FAIL modpipe-{mid:28} gowe bundle: {(b.stderr or b.stdout).strip()[:300]}")
        continue
    body = json.dumps({"name": f"modpipe-{mid}", "cwl": b.stdout}).encode()
    req = urllib.request.Request(f"{a.server.rstrip('/')}/api/v1/workflows/", data=body, method="POST",
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as r:
            d = json.load(r)["data"]
        print(f"ok   modpipe-{mid:28} {d['id']}{'  (unchanged)' if d.get('deduplicated') else ''}")
        registered[mid] = {"name": f"modpipe-{mid}", "id": d["id"], "deduplicated": bool(d.get("deduplicated"))}
    except urllib.error.HTTPError as e:
        failed += 1
        print(f"FAIL modpipe-{mid:28} HTTP {e.code}: {e.read().decode()[:300]}")
if a.json_out:
    with open(a.json_out, "w") as f:
        json.dump(registered, f, indent=1)
sys.exit(1 if failed else 0)
