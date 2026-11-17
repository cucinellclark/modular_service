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
Tool outputs: one per output port, the port's folder in the job result folder (<output_path>/.<output_file>/<port>),
holding one value folder per sample or the value itself. Worker mode: a `string?`, the plain workspace path. As a
Directory a GoWe worker would download the folder for the next step and hand it a local copy without the modpipe_*
metadata (and move every intermediate twice); the next step reads it from the workspace itself. bvbrc mode: a
`Directory?` (glob = port id), which GoWe's BV-BRC executor resolves to ws://<result folder>/<port>.

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
    if mod.service:
        return service_tool_for(mod, ts, dbs)
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
        doc = (f"modpipe type {o.get('type')}: workspace folder <output_path>/.<output_file>/{oid}, one value folder "
               f"per sample (or the value itself), tagged with modpipe_* workspace metadata")
        if mode == "bvbrc":
            outputs[oid] = {"type": ["null", "Directory"], "outputBinding": {"glob": oid}, "doc": doc}
        else:       # a path string: never staged by a worker (see the module doc)
            outputs[oid] = {"type": ["null", "string"], "doc": doc}
        outputs[oid]["modpipe:type"] = o.get("type")

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
    _on_worker(tool, r["cpu"], int(r["memory_gb"] * 1024), image, modpipe_home, ["cwl-step", "job.json"])
    tool["arguments"] = ["--cores", "$(runtime.cores)", "--ram-mb", "$(runtime.ram)"]
    return tool


def _on_worker(tool, cpu, ram_mb, image, modpipe_home, args):
    """Worker-mode hints/requirements: the modpipe worker group, the production image, the submitter's token,
    `<modpipe_home>/bin/modpipe <args>` with the CWL inputs in ./job.json."""
    home = modpipe_home or REPO
    tool["hints"] = {
        "gowe:Execution": {"executor": "worker", "worker_group": WORKER_GROUP, "inject_bvbrc_token": True},
        "DockerRequirement": {"dockerPull": image or default_image()},
    }
    tool["requirements"] = {
        "InlineJavascriptRequirement": {},
        "NetworkAccess": {"networkAccess": True},            # the app talks to the Workspace / data API
        "ResourceRequirement": {"coresMin": cpu, "ramMin": ram_mb},
        "EnvVarRequirement": {"envDef": {"MODPIPE_HOME": home}},
        "InitialWorkDirRequirement": {"listing": [{"entryname": "job.json", "entry": "$(JSON.stringify(inputs))"}]},
    }
    tool["baseCommand"] = [os.path.join(home, "bin", "modpipe")] + list(args)
    return tool


# ---------------------------------------------------------------- service modules (a whole BV-BRC app as one step)

def service_tool_for(mod, ts, dbs):
    """GoWe BV-BRC-executor tool for a service module: GoWe submits the app (mod.service.app) to the BV-BRC app
    service as the user (no container, no token injection, no blessing). Inputs are workspace path strings (an
    upstream port folder is resolved to its file by the helper_value_file step compile inserts); outputs are the
    app's result files, matched by name in <output_path>/.<output_file>/ ({name} = output_file).
    indexed_genome outputs are not here: compile takes them from the helper_wait_genome step."""
    svc = mod.service
    inputs = {}
    for pid, port in mod.inputs.items():
        inputs[pid] = {"type": "string", "doc": f"workspace path of the {port['type']} file [bvbrc:wstype]",
                       "modpipe:type": port["type"]}
    for pid, p in mod.params.items():
        t = _param_type(p)
        if p.get("type") == "enum" and all(isinstance(x, int) for x in p.get("enum") or []):
            t = "int"                                       # e.g. genetic code: the app wants a number
        d = {"type": ["null", t], "doc": _param_doc(p, dbs)}
        if p.get("default") is not None and p.get("default") != "":
            d["default"] = p["default"]
        inputs[pid] = d
    for k, v in (svc.get("fixed") or {}).items():
        t = "boolean" if isinstance(v, bool) else "int" if isinstance(v, int) else "float" if isinstance(v, float) else "string"
        inputs[k] = {"type": t, "default": v, "doc": "fixed by the modpipe module"}
    inputs["output_path"] = {"type": "string", "doc": "Run folder [bvbrc:folder]"}
    inputs["output_file"] = {"type": "string", "doc": "Job name; results in <output_path>/.<output_file>/ [bvbrc:wsid]"}
    outputs = {}
    for oid, o in mod.outputs.items():
        if o.get("indexed_genome"):
            continue
        outputs[oid] = {"type": ["null", "File"], "doc": f"modpipe type {o['type']}",
                        "outputBinding": {"glob": o["path"].replace("{name}", "$(inputs.output_file)")},
                        "modpipe:type": o["type"]}
    label = mod.d.get("label") or mod.id
    return {
        "cwlVersion": "v1.2", "class": "CommandLineTool", "label": label,
        "doc": f"{(mod.d.get('description') or label).strip()}\n\nRuns the BV-BRC app {svc['app']} through GoWe's "
               f"BV-BRC executor (module {mod.id} v{mod.version}); generated by `modpipe export-cwl`.",
        "$namespaces": {"gowe": GOWE_NS, "modpipe": MODPIPE_NS},
        "modpipe:module": mod.id, "modpipe:module_version": mod.version, "modpipe:service": svc["app"],
        "hints": {"gowe:Execution": {"executor": "bvbrc", "bvbrc_app_id": svc["app"]}},
        "baseCommand": [svc["app"]],
        "inputs": inputs, "outputs": outputs,
    }


# ---------------------------------------------------------------- helper tools (worker; inserted by compile)

HELPER_VERSION = 1
HELPERS = {
    "helper_value_file": {
        "label": "modpipe helper: value folder -> file path",
        "doc": "Resolve an upstream port/value folder (modpipe_* metadata) to the workspace path of its one file, for a "
               "service module that takes a file (e.g. contigs for genome annotation). `modpipe gowe-helper value-file`.",
        "inputs": {"value": {"type": "Any", "doc": "workspace path of a port or value folder (or a file)"}},
        "outputs": {"path": {"type": "string"}},
    },
    "helper_wait_genome": {
        "label": "modpipe helper: wait until a genome is indexed",
        "doc": "Read the genome id of an annotated genome (GTO workspace metadata) and wait until BV-BRC has indexed the "
               "genome and its features (data API), then return the id. `modpipe gowe-helper wait-genome`.",
        "inputs": {"gto": {"type": "string", "doc": "workspace path of the annotated genome (.genome, GTO)"},
                   "timeout": {"type": "int", "default": 7200, "doc": "seconds to wait before failing"}},
        "outputs": {"genome_id": {"type": "string"}},
    },
}


def helper_tool(name, image=None, modpipe_home=None):
    h = HELPERS[name]
    tool = {"cwlVersion": "v1.2", "class": "CommandLineTool", "label": h["label"], "doc": h["doc"],
            "$namespaces": {"gowe": GOWE_NS, "modpipe": MODPIPE_NS},
            "modpipe:helper": name, "modpipe:helper_version": HELPER_VERSION,
            "inputs": dict(h["inputs"]), "outputs": dict(h["outputs"])}
    _on_worker(tool, 1, 1024, image, modpipe_home, ["gowe-helper", name[len("helper_"):].replace("_", "-"), "job.json"])
    return tool


def dump(tool):
    """YAML text for a tool (stable key order: CWL header first)."""
    # No `id`: GoWe files an unbundled tool with an id under that id, so a workflow step's `run: <path>` then
    # doesn't resolve. The module id is in modpipe:module; GoWe names registered workflows at registration.
    head = ["cwlVersion", "class", "label", "doc", "$namespaces", "modpipe:module", "modpipe:module_version",
            "modpipe:service", "modpipe:helper", "modpipe:helper_version", "hints", "requirements", "baseCommand", "arguments", "inputs", "outputs"]
    ordered = {k: tool[k] for k in head if k in tool}
    ordered.update({k: v for k, v in tool.items() if k not in ordered})
    return yaml.safe_dump(ordered, sort_keys=False, width=110, allow_unicode=True)


def export(mods, ts, dbs, out_dir, modules=None, **kw):
    """One tool per module (service modules: a BV-BRC-executor tool); in worker mode also the helper tools
    (helper_*.cwl) that compile inserts around service steps."""
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
    if kw.get("mode", "worker") == "worker":
        for name in HELPERS:
            path = os.path.join(out_dir, f"{name}.cwl")
            with open(path, "w") as f:
                f.write(dump(helper_tool(name, kw.get("image"), kw.get("modpipe_home"))))
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
    """cwl.output.json content from the app's modpipe_step_result.json: the workspace path of each produced
    port folder (a string; see the module doc), None for ports not produced."""
    folder = result["result_folder"].rstrip("/")
    values = result.get("values") or {}
    return {oid: (f"{folder}/{oid}" if values.get(oid) else None) for oid in mod.outputs}


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
