#!/usr/bin/env python3
"""Combine P1 (index.json), P2 (invocations_index.json), P3 (nfcore_index.json) into reference/tools/SUMMARY.md.

    python3 tools/build_tool_summary.py tools/tool_list.json reference/tools
"""
import json, os, sys


def load(p, default):
    return json.load(open(p)) if os.path.exists(p) else default


def main(tool_list, d):
    tools = json.load(open(tool_list))["tools"]
    p1 = load(os.path.join(d, "index.json"), {"tools": {}})
    p2 = load(os.path.join(d, "invocations_index.json"), {"tools": {}})
    p3 = load(os.path.join(d, "nfcore_index.json"), {"tools": {}})
    out = ["# Tool metadata summary", "",
           f"- P1 introspection: generated {p1.get('generated')} in `{p1.get('container')}`",
           f"- P2 BV-BRC invocations: {p2.get('files_scanned')} files scanned under `{p2.get('root')}`",
           f"- P3 nf-core modules: commit `{p3.get('commit')}`", "",
           "Per tool: `<id>/version.txt`, `<id>/help.txt`, `<id>/bvbrc_invocations.md`, `<id>/nfcore/<module>/{meta.yml,main.nf}`.", "",
           "| id | category | version | path | help | BV-BRC refs (hunks/files) | nf-core modules | notes |",
           "|---|---|---|---|---|---|---|---|"]
    for t in sorted(tools, key=lambda t: (t.get("category", ""), t["id"])):
        tid = t["id"]
        a = p1["tools"].get(tid, {})
        b = p2["tools"].get(tid, {})
        c = p3["tools"].get(tid, [])
        status = a.get("status", "?")
        ver = a.get("version") or ("MISSING" if status == "missing" else "?")
        help_ok = "yes" if a.get("help_bytes", 0) > 150 else "no"
        refs = f"{b.get('hunks', 0)}/{len(b.get('files', []))}"
        notes = (a.get("notes", "") or t.get("notes", "")).replace("|", "\\|")
        out.append(f"| {tid} | {t.get('category','')} | {ver} | `{a.get('path') or ''}` | {help_ok} | {refs} | "
                   f"{', '.join(c) or 'none'} | {notes} |")
    with open(os.path.join(d, "SUMMARY.md"), "w") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
