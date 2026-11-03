#!/usr/bin/env python3
"""P1: tool introspection snapshot. Run INSIDE the BV-BRC container:

    singularity exec $SIF python3 tools/harvest_tool_info.py tools/tool_list.json reference/tools

For each tool, writes <out>/<id>/version.txt, help.txt, and adds an entry to <out>/index.json.
Tries several version/help flags because tools are inconsistent; keeps the first useful output.
"""
import json, os, shutil, subprocess, sys, time, re

VERSION_FLAGS = [["--version"], ["-version"], ["-v"], ["version"], ["-V"]]
HELP_FLAGS = [["--help"], ["-h"], ["help"], []]
TIMEOUT = 30
VERSION_RE = re.compile(r"\d+(?:\.\d+)+[a-z]?")


def run(cmd):
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           stdin=subprocess.DEVNULL, timeout=TIMEOUT)
        return p.returncode, p.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return None, "<timeout>"
    except OSError as e:
        return None, f"<error: {e}>"


def run_shell(cmd):
    return run(["bash", "-c", cmd])


def pick_version(text, binary):
    """Prefer a version on a line mentioning 'version' or the tool name; else first match."""
    lines = text.splitlines()
    for pref in (lambda l: "version" in l.lower(), lambda l: binary.lower().split(".")[0] in l.lower(), lambda l: True):
        for l in lines:
            m = VERSION_RE.search(l)
            if m and pref(l) and "unrecognized" not in l.lower():
                return m.group(0), l.strip()
    return None, ""


def first_good(path, flag_sets, good):
    tried = []
    for flags in flag_sets:
        rc, out = run([path] + flags)
        tried.append(" ".join(flags) or "<no args>")
        if good(out):
            return " ".join(flags), rc, out, tried
    return None, None, "", tried


def main(tool_list, outdir):
    tools = json.load(open(tool_list))["tools"]
    os.makedirs(outdir, exist_ok=True)
    index = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
             "container": os.environ.get("SINGULARITY_CONTAINER") or os.environ.get("APPTAINER_CONTAINER"),
             "tools": {}}
    for t in tools:
        tid, binary = t["id"], t["binary"]
        path = t.get("path") or shutil.which(binary)
        entry = {"binary": binary, "category": t.get("category"), "path": path,
                 "resolved_path": os.path.realpath(path) if path else None}
        d = os.path.join(outdir, tid)
        os.makedirs(d, exist_ok=True)
        if not path:
            entry["status"] = "missing"
            index["tools"][tid] = entry
            print(f"{tid:18s} MISSING", flush=True)
            continue
        if t.get("notes"):
            entry["notes"] = t["notes"]
        if t.get("version_cmd"):
            vflag, (vrc, vout) = "cmd: " + t["version_cmd"], run_shell(t["version_cmd"])
        else:
            vflag, vrc, vout, _ = first_good(
                path, VERSION_FLAGS + [[]],
                lambda o: bool(VERSION_RE.search(o)) and len(o) < 4000 and "<timeout>" not in o
                and "unrecognized" not in o.lower())
        htried = None
        if t.get("interactive"):
            hflag, hout = None, "<skipped: interactive tool>"
        elif t.get("help_cmd"):
            hflag, (hrc, hout) = "cmd: " + t["help_cmd"], run_shell(t["help_cmd"])
        else:
            hflag, hrc, hout, htried = first_good(
                path, HELP_FLAGS,
                lambda o: len(o.strip()) > 150 and "<timeout>" not in o)
        version, vline = pick_version(vout or "", binary)
        entry.update({"status": "ok", "version_flag": vflag, "version_line": vline[:200],
                      "version": version,
                      "help_flag": hflag, "help_bytes": len(hout),
                      "help_tried": htried if not hflag else None})
        with open(os.path.join(d, "version.txt"), "w") as f:
            f.write(f"# {path} {vflag}\n{vout}")
        with open(os.path.join(d, "help.txt"), "w") as f:
            f.write(f"# {path} {hflag}\n{hout}")
        index["tools"][tid] = entry
        print(f"{tid:18s} v={entry['version']!s:10s} help={hflag!s:8s} {len(hout)}B", flush=True)
    with open(os.path.join(outdir, "index.json"), "w") as f:
        json.dump(index, f, indent=1, sort_keys=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
