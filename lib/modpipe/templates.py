"""Curated pipeline templates: fill a template's inputs and its exposed parameters (template-picker UI path)."""
import copy
import os

from .util import read_json, repo_path


class TemplateError(Exception):
    pass


def find_template(name):
    for cand in (name, repo_path("pipelines", name), repo_path("pipelines", f"{name}.json")):
        if os.path.isfile(cand):
            return cand
    raise TemplateError(f"unknown pipeline template {name!r} (looked in {repo_path('pipelines')})")


def instantiate(template, inputs=None, params=None):
    """Return a concrete pipeline: template with `inputs` {name: source | {source, collection, attributes}}
    and `params` {"<step>.params.<id>": value}. Every template input must be supplied; only exposed params may be set."""
    t = read_json(find_template(template)) if isinstance(template, str) else copy.deepcopy(template)
    p = copy.deepcopy(t)
    inputs, params = inputs or {}, params or {}
    unknown = sorted(set(inputs) - set(p.get("inputs") or {}))
    if unknown:
        raise TemplateError(f"template has no inputs {unknown} (inputs: {sorted(p.get('inputs') or {})})")
    missing = sorted(set(p.get("inputs") or {}) - set(inputs))
    if missing:
        raise TemplateError(f"template inputs not supplied: {missing}")
    for name, v in inputs.items():
        if not isinstance(v, dict):
            raise TemplateError(f"inputs.{name}: expected a source object")
        d = p["inputs"][name]
        if "source" in v:
            d["source"] = v["source"]
            for k in ("collection", "attributes"):
                if k in v:
                    d[k] = v[k]
        else:
            d["source"] = v
    # optional steps: "<step>.enabled": bool (default from template.optional.<step>.default)
    optional = (t.get("template") or {}).get("optional") or {}
    enabled = {s: bool(o.get("default", True)) for s, o in optional.items()}
    for key in list(params):
        if key.endswith(".enabled"):
            step = key[:-len(".enabled")]
            if step not in optional:
                raise TemplateError(f"step {step!r} is not optional in this template (optional: {sorted(optional)})")
            enabled[step] = bool(params.pop(key))
    disabled = {s for s, on in enabled.items() if not on}
    if disabled:
        bypass = {}
        for st in disabled:
            for port, ref in (optional[st].get("bypass") or {}).items():
                bypass[f"{st}.{port}"] = ref
        _remove_steps(p, disabled, bypass)
    exposed = {e for e in ((t.get("template") or {}).get("expose") or []) if e.split(".", 1)[0] not in disabled}
    for key, val in params.items():
        if key not in exposed:
            raise TemplateError(f"parameter {key!r} is not exposed by this template (exposed: {sorted(exposed)})")
        step, _, pid = key.split(".", 2)
        p["steps"][step].setdefault("params", {})[pid] = val
    # links: {"<step>.params.<id>": "<step>.params.<id>"} copies the source value (set or default) to the target,
    # e.g. bracken must use the same database as kraken2.
    for target, source in ((t.get("template") or {}).get("links") or {}).items():
        sstep, _, sid = source.split(".", 2)
        tstep, _, tid = target.split(".", 2)
        if sstep in disabled or tstep in disabled:
            continue
        val = (p["steps"][sstep].get("params") or {}).get(sid)
        if val is None:
            continue  # source uses its module default; target keeps its own default (validator checks consistency)
        p["steps"][tstep].setdefault("params", {})[tid] = val
    p.pop("template", None)
    p["description"] = (p.get("description") or "") + f" [from template {os.path.basename(str(template))}]"
    return p


def _remove_steps(p, disabled, bypass=None):
    """Drop disabled optional steps. References to their outputs are rewired via `bypass` ({"<step>.<port>": ref},
    e.g. primer trimming off -> use the untrimmed BAM); otherwise dropped from list (many) inputs and pipeline
    outputs. A remaining single-valued input that still needs a disabled step is an error."""
    bypass = bypass or {}
    for _ in range(len(disabled) + 1):          # resolve chains of bypasses
        bypass = {k: bypass.get(v, v) for k, v in bypass.items()}
    for s in disabled:
        p["steps"].pop(s, None)
    def rewire(ref):
        return bypass.get(ref, ref) if isinstance(ref, str) else ref
    for st in p["steps"].values():
        st["in"] = {k: ([rewire(r) for r in v] if isinstance(v, list) else rewire(v)) for k, v in (st.get("in") or {}).items()}
    p["outputs"] = {k: rewire(v) for k, v in (p.get("outputs") or {}).items()}
    gone = lambda ref: isinstance(ref, str) and ref.split(".", 1)[0] in disabled
    for sid, st in p["steps"].items():
        for port, ref in list((st.get("in") or {}).items()):
            if isinstance(ref, list):
                kept = [r for r in ref if not gone(r)]
                if kept:
                    st["in"][port] = kept
                else:
                    del st["in"][port]
            elif gone(ref):
                raise TemplateError(f"step {sid!r} needs {ref} from a disabled optional step; enable it")
    p["outputs"] = {k: v for k, v in (p.get("outputs") or {}).items() if not gone(v)}
