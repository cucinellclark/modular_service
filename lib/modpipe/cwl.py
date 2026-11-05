"""CWL export: one CommandLineTool per module, each running the ModularStep app (GoWe workflows chain them).

    modpipe export-cwl [--out DIR] [--mode worker|bvbrc] [--image SIF] [--modpipe-home DIR] [module ...]

Tool inputs mirror App-ModularStep's flat params (lib/modpipe/step.py):
    module                    string, fixed to the module id (default)
    <input port>              Any: a workspace path / ws:// File or Directory (an earlier step's output folder),
                              a list of those, or a pipeline source object. Typed by modpipe, not CWL: the step
                              is validated again inside the job (`modpipe step-pipeline`).
    <parameter>               typed (int/float/boolean/string/enum), optional, module default as CWL default
    input_types               Any (optional {port: concrete type})
    output_path, output_file  the BV-BRC framework params
Tool outputs: one `Directory?` per output port, the port's folder in the job result folder
(ws://<output_path>/.<output_file>/<port>), holding one value folder per sample or the value itself.

Modes:
    worker  run on a GoWe worker: Apptainer image + `modpipe cwl-step` (this checkout, bind-mounted) runs the app
            with the submitter's token (gowe:Execution.inject_bvbrc_token) and reports outputs via cwl.output.json
    bvbrc   submit to the BV-BRC scheduler (gowe:Execution bvbrc_app_id ModularStep), once the app is registered
"""
import json
import os

import yaml

from .util import REPO, repo_path

GOWE_NS = "https://github.com/wilke/GoWe#"
MODPIPE_NS = "https://github.com/cucinellclark/modular_service#"
WORKER_GROUP = "modpipe"


def default_image():
    p = repo_path("singularity_container_ref.txt")
    return open(p).read().strip() if os.path.exists(p) else "ubuntu-176-build12-2.sif"


def _param_type(p):
    t = p.get("type")
    if t == "enum":
        return {"type": "enum", "symbols": [str(s) for s in p.get("enum") or []]}
    return {"int": "int", "float": "float", "bool": "boolean"}.get(t, "string")


def _param_doc(p, dbs):
    bits = [p.get("label") or ""]
    if p.get("description"):
        bits.append(p["description"])
    rng = [f"{k} {p[k]}" for k in ("min", "max") if k in p]
    if rng:
        bits.append(", ".join(rng))
    if p.get("pattern"):
        bits.append(f"pattern {p['pattern']}")
    if p.get("type") == "database":
        choices = sorted(e["id"] for e in dbs.dbs.values() if str(e.get("type", "")).startswith(p.get("db_type", "-")))
        bits.append(f"database ({p.get('db_type')})" + (f": {', '.join(choices)}" if choices else ""))
    return ". ".join(b for b in bits if b)


def _port_doc(port, ts):
    t = port["type"]
    many = port.get("cardinality") == "many"
    d = (f"modpipe type {t}{' (list)' if many else ''}. A workspace path (file, or an output folder of an earlier "
         f"step), a list of them, or a source object (paired_end_libs, srr_ids, genome_ids, ...)")
    if port.get("description"):
        d = f"{port['description']}. {d}"
    return d


def tool_for(mod, ts, dbs, mode="worker", image=None, modpipe_home=None):
    """CWL v1.2 CommandLineTool (dict) for one module."""
    r = mod.resources
    inputs = {"module": {"type": "string", "default": mod.id, "doc": "Module id (fixed for this tool)"}}
    for pid, port in mod.inputs.items():
        required = port.get("required", True) is not False
        inputs[pid] = {"type": "Any" if required else ["null", "Any"], "doc": _port_doc(port, ts),
                       "modpipe:type": port["type"]}
        if port.get("cardinality") == "many":
            inputs[pid]["modpipe:cardinality"] = "many"
    for pid, p in mod.params.items():
        d = {"type": ["null", _param_type(p)], "doc": _param_doc(p, dbs)}
        if p.get("default") is not None and p.get("default") != "":
            d["default"] = p["default"]
        inputs[pid] = d
    inputs["input_types"] = {"type": ["null", "Any"],
                             "doc": "Optional {port: concrete modpipe type} for inputs whose type can't be inferred"}
    inputs["output_path"] = {"type": "string", "doc": "Workspace folder for the results [bvbrc:folder]"}
    inputs["output_file"] = {"type": "string", "doc": "Job name; outputs go to <output_path>/.<output_file>/ [bvbrc:wsid]"}

    outputs = {}
    for oid, o in mod.outputs.items():
        outputs[oid] = {"type": ["null", "Directory"], "outputBinding": {"glob": oid},
                        "doc": f"modpipe type {o.get('type')}: folder <result>/{oid}, one value folder per sample "
                               f"(or the value itself), tagged with modpipe_* workspace metadata",
                        "modpipe:type": o.get("type")}

    label = mod.d.get("label") or mod.id
    doc = (mod.d.get("description") or label).strip()
    tool = {
        "cwlVersion": "v1.2",
        "class": "CommandLineTool",
        "label": label,
        "doc": f"{doc}\n\nRuns BV-BRC app ModularStep (module {mod.id} v{mod.version}); generated by `modpipe export-cwl`.",
        "$namespaces": {"gowe": GOWE_NS, "modpipe": MODPIPE_NS},
        "modpipe:module": mod.id,
        "modpipe:module_version": mod.version,
        "inputs": inputs,
        "outputs": outputs,
    }
    if mode == "bvbrc":
        tool["hints"] = {"gowe:Execution": {"executor": "bvbrc", "bvbrc_app_id": "ModularStep"}}
        tool["baseCommand"] = ["ModularStep"]
        return tool
    if mode != "worker":
        raise ValueError(f"unknown mode {mode!r} (worker or bvbrc)")
    home = modpipe_home or REPO
    tool["hints"] = {
        "gowe:Execution": {"executor": "worker", "worker_group": WORKER_GROUP, "inject_bvbrc_token": True},
        "DockerRequirement": {"dockerPull": image or default_image()},
    }
    tool["requirements"] = {
        "InlineJavascriptRequirement": {},
        "NetworkAccess": {"networkAccess": True},            # the app talks to the Workspace / data API
        "ResourceRequirement": {"coresMin": r["cpu"], "ramMin": int(r["memory_gb"] * 1024)},
        "EnvVarRequirement": {"envDef": {"MODPIPE_HOME": home}},
        "InitialWorkDirRequirement": {"listing": [{"entryname": "job.json", "entry": "$(JSON.stringify(inputs))"}]},
    }
    tool["baseCommand"] = [os.path.join(home, "bin", "modpipe"), "cwl-step", "job.json"]
    tool["arguments"] = ["--cores", "$(runtime.cores)", "--ram-mb", "$(runtime.ram)"]
    return tool


def dump(tool):
    """YAML text for a tool (stable key order: CWL header first)."""
    # No `id`: GoWe files an unbundled tool with an id under that id, so a workflow step's `run: <path>` then
    # doesn't resolve. The module id is in modpipe:module; GoWe names registered workflows at registration.
    head = ["cwlVersion", "class", "label", "doc", "$namespaces", "modpipe:module", "modpipe:module_version",
            "hints", "requirements", "baseCommand", "arguments", "inputs", "outputs"]
    ordered = {k: tool[k] for k in head if k in tool}
    ordered.update({k: v for k, v in tool.items() if k not in ordered})
    return yaml.safe_dump(ordered, sort_keys=False, width=110, allow_unicode=True)


def export(mods, ts, dbs, out_dir, modules=None, **kw):
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for mid in modules or sorted(mods.modules):
        m = mods.get(mid)
        if m is None:
            raise KeyError(f"unknown module {mid}")
        path = os.path.join(out_dir, f"{mid}.cwl")
        with open(path, "w") as f:
            f.write(dump(tool_for(m, ts, dbs, **kw)))
        written.append(path)
    return written


# ---------------------------------------------------------------- worker-side shim: modpipe cwl-step

def _flatten(v):
    """CWL job values -> App-ModularStep params: File/Directory objects -> their workspace/local path."""
    if isinstance(v, dict):
        if v.get("class") in ("File", "Directory"):
            loc = v.get("location") or v.get("path") or ""
            for scheme in ("ws://", "file://"):
                if loc.startswith(scheme):
                    loc = loc[len(scheme):]
            return loc
        return {k: _flatten(x) for k, x in v.items() if x is not None}
    if isinstance(v, list):
        return [_flatten(x) for x in v]
    return v


def app_params(job):
    return {k: _flatten(v) for k, v in job.items() if v is not None}


def cwl_outputs(result, mod):
    """cwl.output.json content from the app's modpipe_step_result.json."""
    folder = result["result_folder"].rstrip("/")
    values = result.get("values") or {}
    out = {}
    for oid in mod.outputs:
        out[oid] = ({"class": "Directory", "location": f"ws://{folder}/{oid}", "basename": oid}
                    if values.get(oid) else None)
    return out


def run_step(job_path, cores=None, ram_mb=None, workdir="."):
    """Run App-ModularStep for a CWL job file; write cwl.output.json. Returns the exit code."""
    import subprocess
    import sys
    from .registry import DatabaseRegistry, ModuleRegistry
    from .types import TypeSystem

    with open(job_path) as f:
        job = json.load(f)
    params = app_params(job)
    ts = TypeSystem()
    mods = ModuleRegistry(ts, DatabaseRegistry())
    mod = mods.get(params.get("module"))
    if mod is None:
        print(f"cwl-step: unknown module {params.get('module')!r}", file=sys.stderr)
        return 2
    app_dir = os.path.abspath(os.path.join(workdir, "app"))
    os.makedirs(app_dir, exist_ok=True)
    pfile = os.path.join(app_dir, "params.json")
    with open(pfile, "w") as f:
        json.dump(params, f, indent=1)

    env = dict(os.environ)
    env["MODPIPE_HOME"] = env.get("MODPIPE_HOME") or REPO
    env["PERL5LIB"] = ":".join(x for x in ("/opt/p3/deployment/lib", env.get("PERL5LIB")) if x)
    if cores:
        env["P3_ALLOCATED_CPU"] = str(cores)
    if ram_mb:
        env["P3_ALLOCATED_MEMORY"] = f"{int(float(ram_mb))}M"
    # GoWe injects the submitter's token as BVBRC_TOKEN / KB_AUTH_TOKEN; AppScript reads P3_AUTH_TOKEN/KB_AUTH_TOKEN.
    tok = env.get("P3_AUTH_TOKEN") or env.get("KB_AUTH_TOKEN") or env.get("BVBRC_TOKEN")
    if not tok:
        print("cwl-step: no BV-BRC token in the environment (BVBRC_TOKEN / KB_AUTH_TOKEN)", file=sys.stderr)
        return 2
    env["P3_AUTH_TOKEN"] = env["KB_AUTH_TOKEN"] = tok
    home = env["MODPIPE_HOME"]
    cmd = ["perl", os.path.join(home, "service-scripts", "App-ModularStep.pl"), "xx",
           os.path.join(home, "app_specs", "ModularStep.json"), pfile]
    print("cwl-step: " + " ".join(cmd), file=sys.stderr, flush=True)
    rc = subprocess.call(cmd, cwd=app_dir, env=env, stdin=subprocess.DEVNULL)

    res_path = os.path.join(app_dir, "modpipe_step_result.json")
    if os.path.exists(res_path):
        with open(res_path) as f:
            result = json.load(f)
        with open(os.path.join(workdir, "cwl.output.json"), "w") as f:
            json.dump(cwl_outputs(result, mod), f, indent=1)
        if rc == 0 and not result.get("ok", True):
            rc = 1
    elif rc == 0:
        print("cwl-step: the app finished but wrote no modpipe_step_result.json", file=sys.stderr)
        rc = 1
    return rc
