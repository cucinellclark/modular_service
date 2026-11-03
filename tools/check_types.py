#!/usr/bin/env python3
"""Validate types/types.yaml, types/wstypes.yaml, resources/databases.yaml (and modules/*.yaml port types),
then report how well the format vocabulary covers the files observed in P4 discovery runs.

    python3 tools/check_types.py            # validate + write reference/types_coverage.md
    python3 tools/check_types.py --quiet    # errors only (exit 1 on errors)

Needs PyYAML (host python or the container).
"""
import collections
import glob
import json
import os
import re
import sys

import yaml

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
P = lambda *a: os.path.join(REPO, *a)
errors, warnings = [], []


def err(m):
    errors.append(m)


def warn(m):
    warnings.append(m)


def load():
    types = yaml.safe_load(open(P("types", "types.yaml")))
    ws = yaml.safe_load(open(P("types", "wstypes.yaml")))
    dbs = yaml.safe_load(open(P("resources", "databases.yaml")))
    known = json.load(open(P("reference", "workspace_types_known.json")))["types"]
    registered = {t for t, d in known.items() if d["registered_2021"]}
    observed = {t for t, d in known.items() if d["observed_qa"] or d["observed_home"]}
    return types, ws, dbs, registered, observed


def check_types(t):
    T, F = t["types"], t["formats"]
    attrs = t.get("attributes", {})
    for tid, d in T.items():
        parts = tid.split(".")
        for i in range(1, len(parts)):
            parent = ".".join(parts[:i])
            if parent not in T:
                err(f"type {tid}: parent {parent} is not defined")
        fmts = []
        if "format" in d:
            fmts.append(d["format"])
        fmts += d.get("formats", [])
        for pname, pv in (d.get("parts") or {}).items():
            if isinstance(pv, str):
                fmts.append(pv)
            else:
                fmts += pv.get("formats", [])
        for f in fmts:
            if f not in F:
                err(f"type {tid}: unknown format {f}")
        for a in (d.get("attributes") or {}):
            if a not in attrs:
                err(f"type {tid}: unknown attribute {a}")
        if not d.get("abstract") and "kind" not in d:
            err(f"type {tid}: concrete type needs a kind")
        if d.get("kind") in ("file",) and not fmts:
            err(f"type {tid}: file kind needs format(s)")
    for c in t.get("converters", []):
        for k in ("from", "to"):
            if c[k] not in T:
                err(f"converter {c}: unknown type {c[k]}")


def resolve_save(ws_save, tid):
    parts = tid.split(".")
    for i in range(len(parts), 0, -1):
        k = ".".join(parts[:i])
        if k in ws_save:
            return ws_save[k]
    return None


def check_ws(t, ws, registered, observed):
    T = t["types"]
    known_ws = registered | observed
    for k, v in ws["save"].items():
        if k not in T:
            err(f"wstypes.save: unknown type {k}")
        vals = []
        if isinstance(v, str):
            vals = [v]
        elif isinstance(v, dict):
            vals = []
            for pv in list((v.get("parts") or {}).values()):
                vals += list(pv.get("by_format", {}).values()) if isinstance(pv, dict) else [pv]
            vals += list((v.get("by_format") or {}).values())
        for w in vals:
            if w not in known_ws:
                err(f"wstypes.save[{k}]: workspace type {w} is not registered or observed")
    for tid, d in T.items():
        if d.get("abstract") or d.get("registry_only") or d.get("kind") == "value":
            continue
        if resolve_save(ws["save"], tid) is None:
            warn(f"type {tid}: no workspace save mapping (falls back to unspecified)")
    for w, d in ws["accept"].items():
        if w not in known_ws:
            err(f"wstypes.accept: workspace type {w} not registered/observed")
        for c in d.get("candidates", []):
            if c not in T:
                err(f"wstypes.accept[{w}]: unknown type {c}")
    for alias, lst in ws.get("app_spec_aliases", {}).items():
        for w in lst:
            if w not in known_ws:
                err(f"app_spec_aliases[{alias}]: {w} not registered/observed")


def check_dbs(t, dbs):
    T = t["types"]
    ids = set()
    for d in dbs["databases"]:
        if d["id"] in ids:
            err(f"databases: duplicate id {d['id']}")
        ids.add(d["id"])
        if d["type"] not in T:
            err(f"databases[{d['id']}]: unknown type {d['type']}")
        elif not (d["type"].startswith("database.") or d["type"].startswith("index.")):
            err(f"databases[{d['id']}]: type must be database.* or index.*")
        if d.get("bind") and d["bind"] not in dbs["binds"]:
            err(f"databases[{d['id']}]: unknown bind {d['bind']}")
        if d.get("status") not in ("verified", "unverified", "missing"):
            err(f"databases[{d['id']}]: bad status {d.get('status')}")
    return ids


def check_modules(t):
    T = t["types"]
    for f in sorted(glob.glob(P("modules", "*.yaml"))):
        m = yaml.safe_load(open(f))
        for direction in ("inputs", "outputs"):
            for port in m.get(direction) or []:
                if port["type"] not in T:
                    err(f"{os.path.relpath(f, REPO)}: {direction}.{port['id']} unknown type {port['type']}")
                elif direction == "outputs" and T[port["type"]].get("abstract") and not port.get("type_from"):
                    err(f"{os.path.relpath(f, REPO)}: output {port['id']} has abstract type {port['type']} without type_from")


# ------------------------------------------------------------------ coverage vs discovery outputs

COMP = re.compile(r"\.(gz|bgz|bz2|zst)$", re.I)
# Path components that mark tool-internal intermediates (not candidates for module output ports).
INTERNAL = re.compile(r"^(K\d+|tmp|temp|misc|corrected|correction|trimming|unitigging|\d+-[\w-]+|\.\w.*|"
                      r"asm\.\w+Store|pipeline_state|split_input|work|logs?)$")


def shallow(path):
    parts = path.split("/")
    return len(parts) <= 3 and not any(INTERNAL.match(p) for p in parts[:-1])


def ext_index(F):
    idx = collections.defaultdict(set)
    for fid, d in F.items():
        for e in d.get("ext", []):
            idx[e.lower()].add(fid)
    return idx


def classify(path, idx):
    name = COMP.sub("", os.path.basename(path)).lower()
    # try longest multi-dot extension first
    parts = name.split(".")
    for i in range(1, len(parts)):
        e = ".".join(parts[i:])
        if e in idx:
            return e, idx[e]
    return (parts[-1] if len(parts) > 1 else "(none)"), set()


def coverage(t, quiet):
    idx = ext_index(t["formats"])
    runs = [json.load(open(f)) for f in glob.glob(P("reference", "tools", "*", "runs", "*.json"))]
    by_ext = collections.Counter()
    unmapped = collections.defaultdict(lambda: {"n": 0, "kinds": collections.Counter(), "tools": set(), "eg": None, "shallow": 0})
    total = 0
    s_total = s_unmapped = 0
    for r in runs:
        for o in r.get("outputs", []):
            if "size" not in o:
                continue
            total += 1
            sh = shallow(o["path"])
            s_total += sh
            e, fmts = classify(o["path"], idx)
            by_ext[e] += 1
            if not fmts:
                s_unmapped += sh
                u = unmapped[e]
                u["shallow"] += sh
                u["n"] += 1
                u["kinds"][o.get("kind")] += 1
                u["tools"].add(r["tool"])
                u["eg"] = u["eg"] or f"{r['run_id']}:{o['path']}"
    mapped = total - sum(u["n"] for u in unmapped.values())
    lines = ["# Type vocabulary coverage of P4 discovery outputs", "",
             "Generated by `tools/check_types.py`. Each output file from `reference/tools/*/runs/*.json` is matched to a "
             "`types/types.yaml` format by extension (compression suffix stripped).", "",
             f"- runs: {len(runs)}; output files: {total}; matched to a format: {mapped} ({100 * mapped / max(total, 1):.1f}%)",
             f"- top-level outputs only (depth <= 3, outside tool-internal dirs): {s_total - s_unmapped}/{s_total} matched "
             f"({100 * (s_total - s_unmapped) / max(s_total, 1):.1f}%)", "",
             "Unmatched extensions are mostly tool intermediates (SPAdes K-mer dirs, canu stores, CheckV tmp), which",
             "modules will not expose as ports. Fixed-name outputs (e.g. `RAxML_bestTree.run`) don't need an extension",
             "match: module descriptors map output paths to types explicitly. Add a format only for genuinely new formats.", "",
             "| extension | files | top-level | sniffed kinds | tools | example |", "|---|---|---|---|---|---|"]
    for e, u in sorted(unmapped.items(), key=lambda x: (-x[1]["shallow"], -x[1]["n"])):
        lines.append(f"| `{e}` | {u['n']} | {u['shallow']} | {', '.join(f'{k}:{n}' for k, n in u['kinds'].most_common(3))} | "
                     f"{', '.join(sorted(u['tools']))[:80]} | `{u['eg'][:90]}` |")
    with open(P("reference", "types_coverage.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    if not quiet:
        print(f"coverage: {mapped}/{total} discovery output files match a format ({100 * mapped / max(total, 1):.1f}%); "
              f"top-level outputs {s_total - s_unmapped}/{s_total} ({100 * (s_total - s_unmapped) / max(s_total, 1):.1f}%); "
              f"details -> reference/types_coverage.md")


def main():
    quiet = "--quiet" in sys.argv
    t, ws, dbs, registered, observed = load()
    check_types(t)
    check_ws(t, ws, registered, observed)
    ids = check_dbs(t, dbs)
    check_modules(t)
    if not quiet:
        T = t["types"]
        print(f"types: {len(T)} ({sum(1 for d in T.values() if d.get('abstract'))} abstract, "
              f"{sum(1 for d in T.values() if d.get('registry_only'))} registry-only); formats: {len(t['formats'])}; "
              f"converters: {len(t.get('converters', []))}; databases: {len(ids)} "
              f"({collections.Counter(d['status'] for d in dbs['databases'])})")
        coverage(t, quiet)
        for w in warnings:
            print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
