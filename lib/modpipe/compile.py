"""modpipe compile: a validated pipeline -> a GoWe CWL workflow over the per-module tools (modpipe export-cwl).

    modpipe compile <pipeline.json> --out DIR [--tools DIR] [--output-path WS] [--run-name NAME] [--name NAME]

Writes DIR/<name>.cwl (the workflow), DIR/job.json (its inputs) and DIR/tools, a symlink to the released tools the
workflow runs (default: the release `current` points at, resolved, so the workflow is pinned to that release).
Submit with:  gowe submit DIR/<name>.cwl -i DIR/job.json   (gowe bundles the tools in; their blessings apply).

Mapping (docs/GOWE.md):
  pipeline step            one workflow step running tools/<module>.cwl, i.e. one ModularStep job. No CWL scatter:
                           ModularStep runs a sample collection inside the job (a port folder holds one value
                           folder per sample, and the next step expands it again).
  $inputs.<name>           a workflow input (Any); job.json gives {type, source[, attributes]}, so the type is
                           explicit and the step reads the data itself
  <step>.<output>          <step>/<output>: the upstream port folder's workspace path (a string)
  [ref, ...] (many port)   several sources, linkMerge merge_flattened + pickValue all_non_null (an output that
                           wasn't produced is dropped, not passed as null)
  step params              fixed step inputs (defaults); module defaults apply to the rest
  output_file              <run_name>_<step>: results in <output_path>/.<run_name>_<step>/<port>/
  pipeline outputs         workflow outputs, workspace path strings (string?)
"""
import json
import os
import re

import yaml

from .pipeline import Validator, auto_convert

WORKFLOW_REQS = {"StepInputExpressionRequirement": {}, "InlineJavascriptRequirement": {}}
RUN_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")


class CompileError(Exception):
    def __init__(self, errors, warnings=()):
        super().__init__("; ".join(errors))
        self.errors = list(errors)
        self.warnings = list(warnings)


def default_tools_dir():
    base = os.environ.get("MODPIPE_RELEASE_BASE") or os.path.expanduser("~/GoWeServer/modpipe")
    return os.path.join(base, "current", "cwl", "tools")


def slug(name):
    s = re.sub(r"[^A-Za-z0-9]+", "-", str(name or "pipeline")).strip("-").lower()
    return ("modpipe-" + s)[:64].rstrip("-") or "modpipe-pipeline"


def _tool_version(path):
    try:
        with open(path) as f:
            return (yaml.safe_load(f) or {}).get("modpipe:module_version")
    except (OSError, yaml.YAMLError):
        return None


def _ref_type(ref, p, plan):
    if ref.startswith("$inputs."):
        return (p.get("inputs") or {}).get(ref[len("$inputs."):], {}).get("type")
    sid, _, port = ref.partition(".")
    return (((plan["steps"].get(sid) or {}).get("output_types") or {}).get(port) or {}).get("type")


def _source(ref):
    return ref[len("$inputs."):] if ref.startswith("$inputs.") else ref.replace(".", "/", 1)


def compile_pipeline(p, ts, mods, dbs, tools_dir=None, where="pipeline"):
    """(workflow dict, job-input template dict, info) for a pipeline; raises CompileError.
    The job template holds the pipeline inputs; the caller adds output_path and run_name."""
    v = Validator(ts, mods, dbs)
    p, iss, plan = auto_convert(v, p, where=where)
    if not iss.ok:
        raise CompileError(iss.errors, iss.warnings)
    errors = []
    tools_dir = os.path.realpath(tools_dir or default_tools_dir())
    steps = p["steps"]

    # ---------------------------------------------------------------- inputs (data must be in the workspace)
    wf_inputs, job = {}, {}
    for name, d in (p.get("inputs") or {}).items():
        src = d.get("source") or {}
        if "fixture" in src:
            errors.append(f"inputs.{name}: source 'fixture' is local test data; a GoWe run reads the workspace "
                          f"(give paired_end_libs / srr_ids / wsids / ... with workspace paths)")
            continue
        wf_inputs[name] = {"type": "Any", "doc": f"modpipe type {d['type']}: {{type, source[, attributes]}}"}
        val = {"type": d["type"], "source": src}
        if d.get("attributes"):
            val["attributes"] = d["attributes"]
        job[name] = val
    wf_inputs["output_path"] = {"type": "string", "doc": "Workspace folder for the results"}
    wf_inputs["run_name"] = {"type": "string",
                             "doc": "Prefix of each step's job name: results in <output_path>/.<run_name>_<step>/"}

    # ---------------------------------------------------------------- steps
    wf_steps, multi = {}, False
    for sid in plan["order"]:
        s, st = steps[sid], plan["steps"][sid]
        m = mods.get(st["module"])
        tool = os.path.join(tools_dir, f"{m.id}.cwl")
        if not os.path.exists(tool):
            errors.append(f"steps.{sid}: no released tool {tool} (run deploy/gowe/release.sh)")
        else:
            tv = _tool_version(tool)
            if tv is not None and str(tv) != str(m.version):
                errors.append(f"steps.{sid}: released tool {m.id} is module version {tv}, this checkout has "
                              f"{m.version} (release the current code, or compile against a matching release)")
        step_in = {}
        for port, raw in (s.get("in") or {}).items():
            refs = raw if isinstance(raw, list) else [raw]
            if isinstance(raw, list):
                types = {_ref_type(r, p, plan) for r in refs}
                if len(types) > 1:
                    errors.append(f"steps.{sid}.in.{port}: items of different types {sorted(map(str, types))}; "
                                  f"ModularStep takes one type per list port (split the step, or convert first)")
                step_in[port] = {"source": [_source(r) for r in refs], "linkMerge": "merge_flattened",
                                 "pickValue": "all_non_null"}
                multi = True
            else:
                step_in[port] = _source(raw)
        for k, val in (s.get("params") or {}).items():
            step_in[k] = {"default": val}
        step_in["output_path"] = "output_path"
        step_in["output_file"] = {"source": "run_name", "valueFrom": f'$(self + "_{sid}")'}
        wf_steps[sid] = {"run": f"tools/{m.id}.cwl", "in": step_in, "out": list(m.outputs)}

    # ---------------------------------------------------------------- outputs
    wf_outputs = {}
    for name, ref in (p.get("outputs") or {}).items():
        if ref.startswith("$inputs."):
            errors.append(f"outputs.{name}: a pipeline input is not a step output")
            continue
        wf_outputs[name] = {"type": "string?", "outputSource": _source(ref),
                            "doc": f"workspace folder of {ref} ({_ref_type(ref, p, plan)})"}
    if errors:
        raise CompileError(errors, iss.warnings)

    reqs = dict(WORKFLOW_REQS)
    if multi:
        reqs["MultipleInputFeatureRequirement"] = {}
    wf = {"cwlVersion": "v1.2", "class": "Workflow", "label": p.get("name") or "modpipe pipeline",
          "doc": (p.get("description") or "").strip() + "\n\nGenerated by `modpipe compile`; each step runs the "
                 "ModularStep app (one module per job).",
          "requirements": reqs, "inputs": wf_inputs, "outputs": wf_outputs, "steps": wf_steps}
    info = {"tools_dir": tools_dir, "warnings": iss.warnings, "auto_converters": plan.get("auto_converters") or [],
            "order": plan["order"], "pipeline": p}
    return wf, job, info


def write(out_dir, wf, job, tools_dir, name):
    """Write <out_dir>/<name>.cwl, job.json and the tools symlink. Returns the workflow path."""
    os.makedirs(out_dir, exist_ok=True)
    link = os.path.join(out_dir, "tools")
    if os.path.islink(link):
        os.remove(link)
    elif os.path.exists(link):
        raise CompileError([f"{link} exists and is not a symlink"])
    os.symlink(tools_dir, link)
    wf_path = os.path.join(out_dir, f"{name}.cwl")
    with open(wf_path, "w") as f:
        f.write(yaml.safe_dump(wf, sort_keys=False, width=110, allow_unicode=True))
    with open(os.path.join(out_dir, "job.json"), "w") as f:
        json.dump(job, f, indent=1)
        f.write("\n")
    return wf_path
