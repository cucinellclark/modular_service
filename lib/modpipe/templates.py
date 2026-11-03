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
    exposed = set((t.get("template") or {}).get("expose") or [])
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
        val = (p["steps"][sstep].get("params") or {}).get(sid)
        if val is None:
            continue  # source uses its module default; target keeps its own default (validator checks consistency)
        p["steps"][tstep].setdefault("params", {})[tid] = val
    p.pop("template", None)
    p["description"] = (p.get("description") or "") + f" [from template {os.path.basename(str(template))}]"
    return p
