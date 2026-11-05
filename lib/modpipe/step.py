"""ModularStep: run one module as a BV-BRC job.

The App-ModularStep params are flat, so that a generated CWL tool (one per module) maps 1:1 onto them, both on a GoWe
worker and through GoWe's BV-BRC executor (which passes CWL inputs to start_app as top-level keys):

    module        module id (required)
    output_path   workspace folder (framework)
    output_file   job name; results go to <output_path>/.<output_file>/ (framework)
    input_types   optional {port: concrete type}, for ports whose type can't be inferred
    <input port>  data for that port (see below)
    <param id>    module parameter value

An input port value is one of:
    "<ws path>"                  a file, or a value folder written by an earlier ModularStep/ModularPipeline output
                                 (tagged with modpipe_* metadata, so its type, parts and sample id come along)
    ["<ws path>", ...]           several of those (gathered by a list port, else processed one by one)
    {<source keys>}              a pipeline input source (paired_end_libs, srr_ids, genome_ids, parts, ...)
    {"type": T, "source": {...}} the same with an explicit type

`step_pipeline` turns the params into a one-step modpipe/pipeline/v1 document whose outputs are all of the module's
output ports, so the normal validate -> stage -> run -> upload path does the rest.
"""
import json

from .pipeline import NAME_RE, SOURCE_KEYS, _collection_size
from .util import Issues, read_yaml, repo_path

RESERVED = {"module", "output_path", "output_file", "input_types"}


def is_ws_path(s):
    """'/<user>@<domain>/...' (a workspace path, as opposed to a local file)."""
    if not isinstance(s, str) or not s.startswith("/"):
        return False
    parts = s.split("/")
    return len(parts) > 2 and "@" in parts[1]


def ws_paths_in(params, mod):
    """Workspace path strings given directly as port values (the app looks up their metadata)."""
    out = []
    for pid in mod.inputs:
        v = params.get(pid)
        for x in (v if isinstance(v, list) else [v]):
            if is_ws_path(x):
                out.append(x)
    return out


def _meta_json(meta, key):
    v = (meta or {}).get(key)
    if not v:
        return None
    if isinstance(v, (dict, list)):
        return v
    try:
        return json.loads(v)
    except (TypeError, ValueError):
        return None


def _from_path(path, ws_meta, ts, port_type, accept):
    """(source fragment, type or None, attrs) for one workspace path string."""
    info = (ws_meta or {}).get(path) or {}
    meta = info.get("meta") or {}
    t = meta.get("modpipe_type")
    attrs = _meta_json(meta, "modpipe_attrs") or {}
    sample = meta.get("modpipe_sample")
    files = _meta_json(meta, "modpipe_files")
    if info.get("type") == "folder":
        if not t or not isinstance(files, dict) or not files:
            raise ValueError(f"{path} is a folder but not a modpipe output folder (no modpipe_type/modpipe_files metadata)")
        full = {k: f"{path.rstrip('/')}/{v}" for k, v in files.items()}
        lib = dict(sample_id=sample) if sample else {}
        if set(full) == {"r1", "r2"}:
            return {"paired_end_libs": [{"read1": full["r1"], "read2": full["r2"], **lib}]}, t, attrs
        if set(full) == {"_"}:
            if sample and ts.kind(t) == "file" and ts.is_a(t, "reads"):
                return {"single_end_libs": [{"read": full["_"], **lib}]}, t, attrs
            return {"wsids": [full["_"]]}, t, attrs
        return {"parts": [{**full, **lib}]}, t, attrs
    if not t:
        cands = [c for c in ((accept.get(info.get("type")) or {}).get("candidates") or [])
                 if ts.is_a(c, port_type)]
        t = cands[0] if len(cands) == 1 else None
    if t and meta.get("modpipe_part"):
        raise ValueError(f"{path} is one part ({meta['modpipe_part']}) of a {t}; give its folder instead")
    return {"wsids": [path]}, t, attrs


def _merge(dst, frag):
    for k, v in frag.items():
        if isinstance(v, list):
            dst.setdefault(k, []).extend(v)
        else:
            dst[k] = v


def _infer_type(ts, port_type, src):
    if not ts.is_abstract(port_type):
        return port_type
    for key, t in (("paired_end_libs", "reads.short.paired"), ("srr_ids", "reads.short.paired"),
                   ("srr_libs", "reads.short.paired"), ("single_end_libs", "reads.short.single")):
        if key in src and ts.is_a(t, port_type):
            return t
    subs = [x for x in ts.types if ts.is_a(x, port_type) and not ts.is_abstract(x) and not ts.is_registry_only(x)]
    return subs[0] if len(subs) == 1 else None


def step_pipeline(params, ts, mods, ws_meta=None):
    """(pipeline dict or None, Issues) for App-ModularStep params. ws_meta: {ws path: {"type": wstype, "meta": {...}}}."""
    iss = Issues()
    mid = params.get("module")
    mod = mods.get(mid) if isinstance(mid, str) else None
    if mod is None:
        iss.error("module", f"unknown module {mid!r}" if mid else "module is required")
        return None, iss
    accept = (read_yaml(repo_path("types", "wstypes.yaml")) or {}).get("accept") or {}
    input_types = params.get("input_types") or {}
    if not isinstance(input_types, dict):
        iss.error("input_types", "must be an object {port: type}")
        input_types = {}
    for k in input_types:
        if k not in mod.inputs:
            iss.error(f"input_types.{k}", f"{mid} has no input port {k!r}")

    for k in params:
        if k in RESERVED or k.startswith("_") or k in mod.inputs or k in mod.params:
            continue
        iss.error(k, f"{mid} has no input port or parameter {k!r} "
                     f"(inputs: {sorted(mod.inputs)}; parameters: {sorted(mod.params)})")

    inputs, step_in = {}, {}
    for pid, port in mod.inputs.items():
        v = params.get(pid)
        w = pid
        if v is None or v == [] or v == "":
            if port.get("required", True) is not False:
                iss.error(w, f"required input {pid} ({port['type']}) is missing")
            continue
        src, t, attrs = {}, None, {}
        try:
            if isinstance(v, dict) and ("source" in v or "type" in v):
                src, t, attrs = dict(v.get("source") or {}), v.get("type"), dict(v.get("attributes") or {})
            elif isinstance(v, dict):
                src = dict(v)
            else:
                types = set()
                for x in (v if isinstance(v, list) else [v]):
                    if not isinstance(x, str):
                        raise ValueError("list items must be workspace paths")
                    frag, ft, fa = _from_path(x, ws_meta, ts, port["type"], accept)
                    _merge(src, frag)
                    if ft:
                        types.add(ft)
                        attrs.update(fa)
                if len(types) > 1:
                    raise ValueError(f"the items have different types {sorted(types)}")
                t = types.pop() if types else None
        except ValueError as e:
            iss.error(w, str(e))
            continue
        unknown = set(src) - SOURCE_KEYS
        if unknown:
            iss.error(w, f"unknown source keys {sorted(unknown)} (known: {sorted(SOURCE_KEYS)})")
            continue
        t = input_types.get(pid) or t or _infer_type(ts, port["type"], src)
        if not t:
            iss.error(w, f"cannot tell which kind of {port['type']} this is; set input_types.{pid} "
                         f"(e.g. one of {sorted(x for x in ts.types if ts.is_a(x, port['type']) and not ts.is_abstract(x))[:6]})")
            continue
        d = {"type": t, "source": src}
        if attrs:
            d["attributes"] = {a: x for a, x in attrs.items() if a in ts.attributes}
        # Several items, or items with sample ids (SRA accessions are sample ids): keep the per-sample layout
        # <output>/<sample>/ so the sample id travels on to the next step.
        if ((_collection_size(src) or 1) > 1 or src.get("srr_ids") or src.get("srr_libs")
                or any(lib.get("sample_id") for key in ("paired_end_libs", "single_end_libs", "parts")
                       for lib in (src.get(key) or []) if isinstance(lib, dict))):
            d["collection"] = True
        inputs[pid] = d
        step_in[pid] = f"$inputs.{pid}"

    step_params = {k: params[k] for k in mod.params if k in params and params[k] is not None}
    sid = mid if NAME_RE.match(mid) else "step"
    p = {"schema": "modpipe/pipeline/v1", "name": f"ModularStep {mid}",
         "description": f"One {mid} step (App-ModularStep)",
         "inputs": inputs,
         "steps": {sid: {"module": mid, "in": step_in, **({"params": step_params} if step_params else {})}},
         "outputs": {o: f"{sid}.{o}" for o in mod.outputs}}
    return (p if iss.ok else None), iss


NEVER_PRODUCED = "is never produced with these parameters"


def build(params, ts, mods, dbs, ws_meta=None):
    """step_pipeline + validation (with automatic converters). Outputs that the module's `when:` rules switch off
    for these parameters are dropped rather than reported. Returns (pipeline or None, Issues)."""
    from .pipeline import Validator, auto_convert
    p, iss = step_pipeline(params, ts, mods, ws_meta)
    if p is None:
        return None, iss
    v = Validator(ts, mods, dbs)
    p2, viss, _ = auto_convert(v, p, where="step")
    off = {it["where"].split(".", 1)[1] for it in viss.items
           if it["severity"] == "error" and it["where"].startswith("outputs.") and NEVER_PRODUCED in it["msg"]}
    if off:
        p = dict(p, outputs={k: r for k, r in p["outputs"].items() if k not in off})
        p2, viss, _ = auto_convert(v, p, where="step")
    iss.extend(viss)
    return (p2 if iss.ok else None), iss
