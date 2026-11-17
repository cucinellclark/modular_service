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
  output_path, output_file the run folder and the step id: results in <run folder>/.<step>/<port>/ (one folder per
                           run; the Workspace creates it with the first step's result folder)
  pipeline outputs         workflow outputs, workspace path strings (string?)
"""
import json
import os
import re

import yaml

from .pipeline import Validator, auto_convert

WORKFLOW_REQS = {}
# CWL expression: a service step's File output (ws:// location) -> the plain workspace path, element-wise for lists
STRIP_WS = ("${var f = function (x) { return (x && typeof x === 'object' && x.location) ? "
            "x.location.replace(/^ws:\\/\\//, '') : x; }; return Array.isArray(self) ? self.map(f) : f(self); }")
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
    The job template holds the pipeline inputs; the caller adds output_path, the run folder."""
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
    wf_inputs["output_path"] = {"type": "string",
                                "doc": "Run folder (<results folder>/<run name>): step results in <output_path>/.<step>/"}

    # ---------------------------------------------------------------- steps
    # Service modules (a whole BV-BRC app, e.g. genome annotation) run through GoWe's BV-BRC executor:
    #  - their inputs are workspace file paths: a one-file pipeline input is passed as its path; an upstream port
    #    folder goes through a helper_value_file step (<step>_<port>_file) that finds its one file;
    #  - their outputs are File objects (ws:// locations): consumers get the plain path (valueFrom STRIP_WS);
    #  - an indexed_genome output (genome_id) comes from one helper_wait_genome step (<step>_indexed) that waits until
    #    BV-BRC has indexed the genome, inserted only when something uses it.
    wf_steps, multi, need_js = {}, False, False
    gowe_steps = []                         # every workflow step in a sensible order: (id, module or helper)
    svc = {sid: mods.get(st["module"]) for sid, st in plan["steps"].items() if mods.get(st["module"]).service}

    def check_tool(where, name, version=None):
        tool = os.path.join(tools_dir, f"{name}.cwl")
        if not os.path.exists(tool):
            errors.append(f"{where}: no released tool {tool} (run deploy/gowe/release.sh)")
            return
        tv = _tool_version(tool)
        if version is not None and tv is not None and str(tv) != str(version):
            errors.append(f"{where}: released tool {name} is module version {tv}, this checkout has "
                          f"{version} (release the current code, or compile against a matching release)")

    def ensure_wait(s):
        wid = f"{s}_indexed"
        if wid not in wf_steps:
            gto = [o for o, op in svc[s].outputs.items() if op.get("type") == "annotation.gto"]
            if not gto:
                errors.append(f"steps.{s}: {svc[s].id} has an indexed_genome output but no annotation.gto output")
                return f"{wid}/genome_id"
            check_tool(f"steps.{s}", "helper_wait_genome")
            wf_steps[wid] = {"run": "tools/helper_wait_genome.cwl",
                             "in": {"gto": {"source": f"{s}/{gto[0]}", "valueFrom": STRIP_WS}}, "out": ["genome_id"]}
            gowe_steps.append((wid, "helper_wait_genome"))
        return f"{wid}/genome_id"

    def src(ref):
        """(CWL source, is a File object from a service step)"""
        if ref.startswith("$inputs."):
            return ref[len("$inputs."):], False
        s, _, o = ref.partition(".")
        if s in svc:
            if svc[s].outputs.get(o, {}).get("indexed_genome"):
                return ensure_wait(s), False
            return f"{s}/{o}", True
        return f"{s}/{o}", False

    for sid in plan["order"]:
        s, st = steps[sid], plan["steps"][sid]
        m = mods.get(st["module"])
        check_tool(f"steps.{sid}", m.id, m.version)
        step_in = {}
        for port, raw in (s.get("in") or {}).items():
            refs = raw if isinstance(raw, list) else [raw]
            if m.service:
                ref = refs[0]
                if ref.startswith("$inputs."):
                    name = ref[len("$inputs."):]
                    srcd = (p["inputs"].get(name) or {}).get("source") or {}
                    files = srcd.get("wsids") if set(srcd) == {"wsids"} else None
                    if not files or len(files) != 1:
                        errors.append(f"steps.{sid}.in.{port}: {m.id} runs the BV-BRC {m.service['app']} app, which "
                                      f"takes one workspace file; give inputs.{name} as one workspace file (wsids)")
                        continue
                    wf_inputs[f"{name}__file"] = {"type": "string", "doc": f"workspace path of inputs.{name}"}
                    job[f"{name}__file"] = files[0]
                    step_in[port] = f"{name}__file"
                elif ref.split(".", 1)[0] in svc:
                    step_in[port] = {"source": src(ref)[0], "valueFrom": STRIP_WS}
                    need_js = True
                else:
                    hid = f"{sid}_{port}_file"
                    check_tool(f"steps.{sid}", "helper_value_file")
                    wf_steps[hid] = {"run": "tools/helper_value_file.cwl", "in": {"value": _source(ref)}, "out": ["path"]}
                    gowe_steps.append((hid, "helper_value_file"))
                    step_in[port] = f"{hid}/path"
                continue
            if isinstance(raw, list):
                types = {_ref_type(r, p, plan) for r in refs}
                if len(types) > 1:
                    errors.append(f"steps.{sid}.in.{port}: items of different types {sorted(map(str, types))}; "
                                  f"ModularStep takes one type per list port (split the step, or convert first)")
                srcs = [src(r) for r in refs]
                step_in[port] = {"source": [x[0] for x in srcs], "linkMerge": "merge_flattened",
                                 "pickValue": "all_non_null"}
                if any(x[1] for x in srcs):
                    step_in[port]["valueFrom"] = STRIP_WS
                    need_js = True
                multi = True
            else:
                source, is_file = src(raw)
                step_in[port] = {"source": source, "valueFrom": STRIP_WS} if is_file else source
                need_js = need_js or is_file
        for k, val in (s.get("params") or {}).items():
            step_in[k] = {"default": val}
        step_in["output_path"] = "output_path"
        step_in["output_file"] = {"default": sid}
        outs = [o for o, op in m.outputs.items() if not op.get("indexed_genome")]
        wf_steps[sid] = {"run": f"tools/{m.id}.cwl", "in": step_in, "out": outs}
        gowe_steps.append((sid, m.id))

    # ---------------------------------------------------------------- outputs
    wf_outputs = {}
    for name, ref in (p.get("outputs") or {}).items():
        if ref.startswith("$inputs."):
            errors.append(f"outputs.{name}: a pipeline input is not a step output")
            continue
        source, is_file = src(ref)
        wf_outputs[name] = {"type": "File?" if is_file else "string?", "outputSource": source,
                            "doc": f"{'file' if is_file else 'workspace folder'} of {ref} ({_ref_type(ref, p, plan)})"}
    if errors:
        raise CompileError(errors, iss.warnings)

    reqs = dict(WORKFLOW_REQS)
    if multi:
        reqs["MultipleInputFeatureRequirement"] = {}
    if need_js or any(isinstance(v, dict) and "valueFrom" in v for st_ in wf_steps.values() for v in st_["in"].values()):
        reqs["InlineJavascriptRequirement"] = {}
        reqs["StepInputExpressionRequirement"] = {}
    wf = {"cwlVersion": "v1.2", "class": "Workflow", "label": p.get("name") or "modpipe pipeline",
          # no leading blank line: it makes the bundler emit a `|4-` block scalar that GoWe's YAML parser rejects
          "doc": "\n\n".join(x for x in ((p.get("description") or "").strip(),
                                         "Generated by `modpipe compile`; each step runs the ModularStep app (one "
                                         "module per job), service modules run their BV-BRC app.") if x),
          **({"requirements": reqs} if reqs else {}), "inputs": wf_inputs, "outputs": wf_outputs, "steps": wf_steps}
    info = {"tools_dir": tools_dir, "warnings": iss.warnings, "auto_converters": plan.get("auto_converters") or [],
            "order": plan["order"], "pipeline": p, "gowe_steps": gowe_steps}
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
