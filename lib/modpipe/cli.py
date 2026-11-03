"""modpipe command line.

  modpipe lint [module ...]                 validate module descriptors (all if none given)
  modpipe validate <pipeline.json> [--json] validate a pipeline; exit 1 on errors
  modpipe plan <pipeline.json>              validate and print the resolved plan (types, scatter, resources)
  modpipe list-modules [--category C] [--json]
  modpipe show <module>                     ports, parameters, resources of one module
  modpipe compatible --from <module>.<output> | --type <type>
                                            which module inputs can consume this
  modpipe list-templates [--json]           curated pipelines (pipelines/*.json) with inputs and exposed params
  modpipe instantiate <template> [--inputs F] [--params F] [--out F]
                                            fill a curated template (pipelines/<template>.json)
  modpipe serve [--host H] [--port P] [--origin URL ...]
                                            prototype API for the BV-BRC-Web ModularPipeline form
  modpipe run <pipeline.json> --workdir DIR [--executor snakemake|local] [--cores N] [--mem 64G]
                                            [--resume] [--dry-run]   execute (inside the BV-BRC container)
"""
import argparse
import json
import sys

from .pipeline import Validator, auto_convert, load_pipeline
from .registry import DatabaseRegistry, ModuleRegistry
from .types import TypeSystem


def _ctx():
    ts = TypeSystem()
    dbs = DatabaseRegistry()
    mods = ModuleRegistry(ts, dbs)
    return ts, dbs, mods


def cmd_lint(a):
    ts, dbs, mods = _ctx()
    issues = mods.load_issues
    targets = a.modules or sorted(mods.modules)
    nerr = len(issues.errors)
    for mid in targets:
        m = mods.get(mid)
        if m is None:
            print(f"ERROR unknown module {mid}")
            nerr += 1
            continue
        iss = mods.lint(m)
        status = "ok" if iss.ok else "FAIL"
        print(f"[{status}] {mid} v{m.version}  ({len(iss.errors)} errors, {len(iss.warnings)} warnings)")
        iss.report(sys.stdout, quiet=a.quiet)
        nerr += len(iss.errors)
    issues.report(sys.stdout, quiet=a.quiet)
    return 1 if nerr else 0


def _validate(path, auto=True):
    ts, dbs, mods = _ctx()
    p = load_pipeline(path)
    v = Validator(ts, mods, dbs)
    if auto:
        p, iss, plan = auto_convert(v, p, where=path)
    else:
        iss, plan = v.validate(p, where=path)
    plan["pipeline"] = p
    return iss, plan


def cmd_validate(a):
    iss, plan = _validate(a.pipeline, auto=not a.no_auto_convert)
    if a.json:
        print(json.dumps({"ok": iss.ok, "errors": iss.errors, "warnings": iss.warnings, "plan": plan}, indent=1, default=str))
    else:
        iss.report(sys.stdout)
        print(f"{'OK' if iss.ok else 'INVALID'}: {a.pipeline} ({len(iss.errors)} errors, {len(iss.warnings)} warnings)")
    return 0 if iss.ok else 1


def cmd_plan(a):
    iss, plan = _validate(a.pipeline)
    iss.report(sys.stdout)
    for sid in plan["order"]:
        st = plan["steps"].get(sid)
        if not st:
            continue
        sc = f"  [scatter over {st['scatter']} x{st['scatter_size'] or '?'}]" if st["scatter"] else ""
        print(f"{sid}: {st['module']} v{st['module_version']}{sc}")
        for k, v in st["inputs"].items():
            print(f"    in  {k:16s} {v}")
        for k, v in st["outputs"].items():
            print(f"    out {k:16s} {v}")
        for d in st["databases"]:
            print(f"    db  {d['param']:16s} {d['db']} ({d['status']})")
        r = st["resources"]
        est = st.get("estimate") or {}
        par = f"  ({est['parallel']} in parallel, {est['waves']} wave(s))" if st["scatter"] else ""
        print(f"    res cpu={r['cpu']} mem={r['memory_gb']:g}G runtime={r['runtime_s'] / 3600:g}h{par}")
    r = plan.get("resources") or {}
    if r:
        extra = f" partition={r['partition']}" if r.get("partition") else ""
        print(f"\njob request: cpu={r['cpu']} memory={r['memory_gb']:g}G runtime~{r['runtime']}{extra}")
    print("pipeline outputs:", ", ".join(f"{k}={v}" for k, v in plan.get("outputs", {}).items()))
    print(f"{'OK' if iss.ok else 'INVALID'} ({len(iss.errors)} errors, {len(iss.warnings)} warnings)")
    return 0 if iss.ok else 1


def cmd_list(a):
    ts, dbs, mods = _ctx()
    rows = [m.summary() for m in mods.modules.values() if not a.category or m.d.get("category") == a.category]
    if a.json:
        print(json.dumps(rows, indent=1))
        return 0
    for r in sorted(rows, key=lambda r: (r["category"] or "", r["id"])):
        ins = ", ".join(f"{p['id']}:{p['type']}" for p in r["inputs"])
        outs = ", ".join(f"{p['id']}:{p['type']}" for p in r["outputs"])
        print(f"{r['id']:12s} v{r['version']} [{r['category']}] {r['label']}\n    in:  {ins}\n    out: {outs}")
    return 0


def cmd_show(a):
    ts, dbs, mods = _ctx()
    m = mods.get(a.module)
    if not m:
        print(f"unknown module {a.module}")
        return 1
    print(json.dumps(m.summary(), indent=1))
    return 0


def cmd_compatible(a):
    ts, dbs, mods = _ctx()
    if a.from_:
        mid, _, port = a.from_.partition(".")
        m = mods.get(mid)
        if not m or port not in m.outputs:
            print(f"unknown output {a.from_}")
            return 1
        op = m.outputs[port]
        src = op["type"]
        derived = op.get("type_from") is not None
    else:
        src, derived = a.type, False
        if src not in ts:
            print(f"unknown type {src}")
            return 1
    print(f"{a.from_ or src} -> {src}{' (derived from inputs)' if derived else ''}")
    found = 0
    for m in sorted(mods.modules.values(), key=lambda m: m.id):
        for pid, p in m.inputs.items():
            if ts.is_a(src, p["type"]):
                print(f"  yes    {m.id}.{pid} ({p['type']})")
                found += 1
            elif ts.is_a(p["type"], src) and (derived or ts.is_abstract(src)):
                print(f"  maybe  {m.id}.{pid} ({p['type']}; depends on the concrete type)")
                found += 1
            else:
                for c in ts.converters_between(src, p["type"]):
                    print(f"  via    {m.id}.{pid} ({p['type']}) after converter {c['module']}")
                    found += 1
    if not found:
        print("  (no compatible module inputs)")
    return 0


def cmd_serve(a):
    from .api import serve
    serve(a.host, a.port, a.origin or ["http://localhost:3000"])
    return 0


def cmd_list_templates(a):
    import glob
    import os
    from .util import read_json, repo_path
    ts, dbs, mods = _ctx()
    rows = []
    for f in sorted(glob.glob(repo_path("pipelines", "*.json"))):
        p = read_json(f)
        t = p.get("template") or {}
        exposed = []
        for e in t.get("expose") or []:
            step, _, pid = e.split(".", 2)
            m = mods.get(p["steps"][step]["module"])
            spec = dict(m.params.get(pid, {})) if m else {}
            spec.update({"key": e, "module": m.id if m else None})
            exposed.append(spec)
        rows.append({"template": os.path.basename(f)[:-5], "label": t.get("label"), "category": t.get("category"),
                     "optional_steps": {k: {"label": v.get("label", k), "default": v.get("default", True),
                                            "module": p["steps"][k]["module"]} for k, v in (t.get("optional") or {}).items()},
                     "description": p.get("description"),
                     "inputs": {k: {"type": v["type"], "collection": bool(v.get("collection"))} for k, v in p["inputs"].items()},
                     "outputs": sorted(p.get("outputs") or {}), "exposed_params": exposed,
                     "links": t.get("links") or {}})
    if a.json:
        print(json.dumps(rows, indent=1))
        return 0
    for r in rows:
        ins = ", ".join(f"{k}:{v['type']}{'[]' if v['collection'] else ''}" for k, v in r["inputs"].items())
        print(f"{r['template']:36s} [{r['category']}] {r['label']}\n    inputs: {ins}\n    params: "
              + ", ".join(e["key"] for e in r["exposed_params"]))
    return 0


def cmd_instantiate(a):
    from .templates import TemplateError, instantiate
    from .util import read_json
    try:
        p = instantiate(a.template, read_json(a.inputs) if a.inputs else None, read_json(a.params) if a.params else None)
    except TemplateError as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 1
    txt = json.dumps(p, indent=1)
    if a.out:
        with open(a.out, "w") as f:
            f.write(txt + "\n")
    else:
        print(txt)
    return 0


def cmd_run(a):
    from .run import RunError, run_pipeline
    from .util import parse_memory_gb
    ts, dbs, mods = _ctx()
    try:
        rec = run_pipeline(ts, mods, dbs, load_pipeline(a.pipeline), a.workdir, executor=a.executor, cores=a.cores,
                           mem_gb=parse_memory_gb(a.mem) if a.mem else None, resume=a.resume, dry_run=a.dry_run,
                           where=a.pipeline, keep_intermediates=a.keep_intermediates)
    except RunError as e:
        print(f"RUN FAILED: {e}", file=sys.stderr)
        return 1
    if a.dry_run:
        return 0
    print(f"OK: {len(rec['jobs'])} job(s); {len(rec['outputs'])} output file(s) in {a.workdir}/outputs "
          f"(manifest.json); provenance in {a.workdir}/pipeline_run.json")
    for j in rec["jobs"]:
        print(f"  {j['id']:28s} {j['status']:6s} wall={j.get('wall_s', '?')}s rss={j.get('max_rss_mb', '?')}MB")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="modpipe", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("lint")
    s.add_argument("modules", nargs="*")
    s.add_argument("--quiet", action="store_true", help="errors only")
    s.set_defaults(fn=cmd_lint)
    s = sub.add_parser("validate")
    s.add_argument("pipeline")
    s.add_argument("--json", action="store_true")
    s.add_argument("--no-auto-convert", action="store_true", help="report fixable type mismatches instead of inserting converters")
    s.set_defaults(fn=cmd_validate)
    s = sub.add_parser("plan")
    s.add_argument("pipeline")
    s.set_defaults(fn=cmd_plan)
    s = sub.add_parser("list-modules")
    s.add_argument("--category")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_list)
    s = sub.add_parser("show")
    s.add_argument("module")
    s.set_defaults(fn=cmd_show)
    s = sub.add_parser("compatible")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--from", dest="from_", metavar="MODULE.OUTPUT")
    g.add_argument("--type")
    s.set_defaults(fn=cmd_compatible)
    s = sub.add_parser("run")
    s.add_argument("pipeline")
    s.add_argument("--workdir", required=True)
    s.add_argument("--executor", choices=["snakemake", "local"], default="snakemake")
    s.add_argument("--cores", type=int)
    s.add_argument("--mem", help="memory budget, e.g. 64G (default: the plan's estimate)")
    s.add_argument("--resume", action="store_true", help="keep completed jobs")
    s.add_argument("--dry-run", action="store_true", help="stage inputs and write job scripts/Snakefile only")
    s.add_argument("--keep-intermediates", action="store_true", help="also list every step output in the manifest")
    s.set_defaults(fn=cmd_run)
    s = sub.add_parser("serve")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8765)
    s.add_argument("--origin", action="append", help="allowed CORS origin (repeatable; default http://localhost:3000)")
    s.set_defaults(fn=cmd_serve)
    s = sub.add_parser("list-templates")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_list_templates)
    s = sub.add_parser("instantiate")
    s.add_argument("template")
    s.add_argument("--inputs", help="JSON file: {input name: source}")
    s.add_argument("--params", help="JSON file: {\"<step>.params.<id>\": value} (exposed params only)")
    s.add_argument("--out")
    s.set_defaults(fn=cmd_instantiate)
    a = ap.parse_args(argv)
    return a.fn(a)
