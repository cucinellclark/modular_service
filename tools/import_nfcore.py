#!/usr/bin/env python3
"""P3: copy nf-core module metadata (meta.yml, main.nf, environment.yml) for tools in tool_list.json.

    git clone --depth 1 --filter=blob:none --sparse https://github.com/nf-core/modules.git <dir>
    git -C <dir> sparse-checkout set modules/nf-core
    python3 tools/import_nfcore.py <dir> tools/tool_list.json reference/tools

Never executes anything from the clone; only copies text files.
"""
import json, os, shutil, subprocess, sys

def main(nf, tool_list, out):
    base = os.path.join(nf, "modules/nf-core")
    commit = subprocess.check_output(["git", "-C", nf, "log", "-1", "--format=%H %cs"]).decode().strip()
    tools = json.load(open(tool_list))["tools"]
    idx = {"source": "https://github.com/nf-core/modules", "commit": commit, "tools": {}, "missing": []}
    for t in tools:
        got = []
        for m in t.get("nfcore", []):
            src = os.path.join(base, m)
            if not os.path.isdir(src):
                idx["missing"].append([t["id"], m]); continue
            dst = os.path.join(out, t["id"], "nfcore", m.replace("/", "__"))
            os.makedirs(dst, exist_ok=True)
            for f in ("meta.yml", "main.nf", "environment.yml"):
                if os.path.exists(os.path.join(src, f)):
                    shutil.copy(os.path.join(src, f), dst)
            got.append(m)
        idx["tools"][t["id"]] = got
    with open(os.path.join(out, "nfcore_index.json"), "w") as f:
        json.dump(idx, f, indent=1)
    print("commit", commit, "missing", idx["missing"])

if __name__ == "__main__":
    main(*sys.argv[1:4])
