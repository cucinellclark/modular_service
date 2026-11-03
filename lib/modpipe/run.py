"""Run a pipeline end to end in a local directory: validate -> stage -> jobs -> execute -> collect outputs.

Produces in the run directory:
  outputs/<name>[/<sample>]/...   symlinks to the declared pipeline outputs
  outputs/manifest.json           each output with its type and the workspace type to save it as
  pipeline_run.json               provenance: pipeline, plan, module/tool versions, per-job status/time/RSS
Workspace upload is the job of the BV-BRC shell (App-ModularPipeline.pl), not of this module.
"""
import datetime
import json
import os
import re
import socket
import sys

from .executors import ExecutionError, LocalExecutor, SnakemakeExecutor
from .materialize import Materializer, StagingError
from .pipeline import Validator
from .util import read_yaml, repo_path


class RunError(Exception):
    pass


def wstype_for(ts, wst, type_id, part=None, fmt_path=None):
    """Workspace type to save a value of `type_id` (or one of its parts) as; see types/wstypes.yaml `save`."""
    for anc in ts.ancestors(type_id):
        v = wst["save"].get(anc)
        if v is None:
            continue
        if isinstance(v, str):
            return v
        if part and part in (v.get("parts") or {}):
            pv = v["parts"][part]
            if isinstance(pv, dict):          # {by_format: {fmt: wstype}}: pick by file extension
                ext = (fmt_path or "").lower().rsplit(".", 1)[-1]
                for fmt, w in (pv.get("by_format") or {}).items():
                    if ext in [e.lower() for e in ts.formats.get(fmt, {}).get("ext", [])]:
                        return w
                return "unspecified"
            return pv
        if fmt_path and v.get("by_format"):
            ext = fmt_path.lower().rsplit(".", 1)[-1]
            for fmt, w in v["by_format"].items():
                if ext in [e.lower() for e in ts.formats.get(fmt, {}).get("ext", [])]:
                    return w
        if v.get("parts") and not part:
            first = next(iter(v["parts"].values()))
            return first if isinstance(first, str) else "unspecified"
    return "unspecified"


def _parse_time(path):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, errors="replace") as f:
        txt = f.read()
    m = re.search(r"Maximum resident set size \(kbytes\): (\d+)", txt)
    if m:
        out["max_rss_mb"] = round(int(m.group(1)) / 1024, 1)
    m = re.search(r"Elapsed \(wall clock\) time.*: (.+)", txt)
    if m:
        sec = 0.0
        for x in m.group(1).strip().split(":"):
            sec = sec * 60 + float(x)
        out["wall_s"] = round(sec, 2)
    m = re.search(r"Exit status: (\d+)", txt)
    if m:
        out["exit_status"] = int(m.group(1))
    return out


def run_pipeline(ts, mods, dbs, pipeline, rundir, executor="snakemake", cores=None, mem_gb=None,
                 resume=False, dry_run=False, where="pipeline", keep_intermediates=False):
    rundir = os.path.abspath(rundir)
    iss, plan = Validator(ts, mods, dbs).validate(pipeline, where=where)
    iss.report(sys.stderr)
    if not iss.ok:
        raise RunError(f"pipeline is invalid ({len(iss.errors)} errors)")
    res = plan["resources"]
    cores = cores or int(os.environ.get("P3_ALLOCATED_CPU") or os.environ.get("SLURM_CPUS_PER_TASK") or res["cpu"])
    mem_gb = mem_gb or res["memory_gb"]
    os.makedirs(rundir, exist_ok=True)
    started = datetime.datetime.now().isoformat(timespec="seconds")
    mat = Materializer(ts, mods, dbs, pipeline, plan, rundir, cores, mem_gb)
    try:
        mat.stage_inputs()
        jobs = mat.build_jobs()
        mat.write()
    except StagingError as e:
        raise RunError(str(e))
    ex = (SnakemakeExecutor if executor == "snakemake" else LocalExecutor)(cores, mem_gb, resume=resume)
    if dry_run:
        if executor == "snakemake":
            ex.write_snakefile(jobs, rundir)
        print(f"dry run: {len(jobs)} job(s) written under {rundir}", file=sys.stderr)
        return {"jobs": list(jobs), "rundir": rundir}
    error = None
    try:
        ex.run(jobs, rundir)
    except ExecutionError as e:
        error = str(e)
    record = _record(ts, mods, pipeline, plan, mat, jobs, rundir, executor, cores, mem_gb, started, error,
                     keep_intermediates)
    if error:
        raise RunError(error)
    return record


def _record(ts, mods, pipeline, plan, mat, jobs, rundir, executor, cores, mem_gb, started, error,
            keep_intermediates=False):
    wst = read_yaml(repo_path("types", "wstypes.yaml"))
    out_dir = os.path.join(rundir, "outputs")
    manifest = []
    if not error:
        wanted = dict(pipeline.get("outputs") or {})
        if keep_intermediates:
            declared = set(wanted.values())
            for ref in mat.values:
                if not ref.startswith("$inputs.") and ref not in declared:
                    wanted[f"steps/{ref.replace('.', '/', 1)}"] = ref
        for name, ref in wanted.items():
            kind, v = mat.values[ref]
            items = v.items() if kind == "coll" else [(None, v)]
            for sample, val in items:
                if val is None:
                    continue
                d = os.path.join(out_dir, name, sample) if sample else os.path.join(out_dir, name)
                os.makedirs(d, exist_ok=True)
                files = [(None, val._path)] if val._path else list(val._parts.items())
                for part, src in files:
                    if not os.path.exists(src):
                        continue
                    link = os.path.join(d, os.path.basename(src))
                    if os.path.lexists(link):
                        os.remove(link)
                    os.symlink(os.path.relpath(src, d), link)
                    manifest.append({"output": name, "sample": sample, "part": part, "type": val.type,
                                     "attrs": val.attrs, "path": os.path.relpath(link, rundir),
                                     "size": os.path.getsize(src),
                                     "wstype": wstype_for(ts, wst, val.type, part=part, fmt_path=src)})
        with open(os.path.join(out_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=1)
    tool_index = mods.tool_index
    job_records = []
    for j in jobs.values():
        info = _parse_time(os.path.join(j.workdir, ".modpipe", "time.txt"))
        tool = (j.module.d.get("tool") or {})
        job_records.append({"id": j.id, "step": j.step, "sample": j.sample, "module": j.module.id,
                            "module_version": j.module.version, "tool": tool.get("id"),
                            "tool_version_declared": tool.get("version"),
                            "tool_version_container": (tool_index.get(tool.get("id")) or {}).get("version"),
                            "status": "ok" if os.path.exists(j.marker) else "failed_or_not_run",
                            "cpu": j.cpu, "mem_gb": j.mem_gb, "command": j.command, **info})
    rec = {"schema": "modpipe/run/v1", "pipeline": pipeline, "plan_resources": plan["resources"],
           "executor": executor, "cores": cores, "mem_gb": mem_gb, "rundir": rundir, "host": socket.gethostname(),
           "container": os.environ.get("SINGULARITY_CONTAINER") or os.environ.get("APPTAINER_CONTAINER"),
           "slurm_job": os.environ.get("SLURM_JOB_ID"), "started": started,
           "finished": datetime.datetime.now().isoformat(timespec="seconds"),
           "status": "failed" if error else "ok", "error": error, "jobs": job_records, "outputs": manifest}
    with open(os.path.join(rundir, "pipeline_run.json"), "w") as f:
        json.dump(rec, f, indent=1, default=str)
    return rec
