"""Turn a validated pipeline into concrete jobs: stage inputs, expand scatter, render commands, write job scripts.

Layout under the run directory:
  inputs/<name>/...                  staged pipeline inputs (downloads; local files are used in place)
  steps/<step>[/<sample>]/           one job directory per (step, sample)
      .modpipe/cmd.sh                the rendered tool command
      .modpipe/job.sh                wrapper: clean dir, (de)compress inputs, run under /usr/bin/time, check outputs
      .modpipe/done                  completion marker (dependency token for executors)
  .modpipe/jobs.json                 the job graph
"""
import collections
import json
import os
import re
import shlex
import shutil
import subprocess

from .template import Value, build_context, db_context, eval_when, output_value, render_command, resolve_output_type
from .util import parse_memory_gb, read_json, repo_path


class StagingError(Exception):
    pass


class Job:
    def __init__(self, jid, step, sample, module, workdir):
        self.id, self.step, self.sample, self.module, self.workdir = jid, step, sample, module, workdir
        self.deps, self.external_inputs, self.required_outputs = set(), [], []
        self.inputs, self.outputs, self.command, self.cpu, self.mem_gb = {}, {}, None, 1, 1
        self.prelude = []

    @property
    def marker(self):
        return os.path.join(self.workdir, ".modpipe", "done")

    @property
    def script(self):
        return os.path.join(self.workdir, ".modpipe", "job.sh")

    def to_json(self):
        def ser(v):
            if v is None:
                return None
            if isinstance(v, list):
                return [ser(x) for x in v]
            return {"type": v.type, "path": v._path, "parts": v._parts or None, "attrs": v.attrs}
        return {"id": self.id, "step": self.step, "sample": self.sample, "module": self.module.id,
                "module_version": self.module.version, "workdir": self.workdir, "deps": sorted(self.deps),
                "cpu": self.cpu, "mem_gb": self.mem_gb, "command": self.command,
                "inputs": {k: ser(v) for k, v in self.inputs.items()},
                "outputs": {k: ser(v) for k, v in self.outputs.items()},
                "required_outputs": self.required_outputs}


def _compression(path):
    return "gzip" if str(path).endswith((".gz", ".bgz")) else "none"


def _safe(name):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(name))


class Materializer:
    def __init__(self, ts, mods, dbs, pipeline, plan, rundir, cores, mem_gb, container=None, fixtures_index=None):
        self.ts, self.mods, self.dbs = ts, mods, dbs
        self.p, self.plan, self.rundir = pipeline, plan, os.path.abspath(rundir)
        self.cores, self.mem_gb, self.container = cores, mem_gb, container
        fi = fixtures_index or repo_path("tests", "fixtures", "data", "fixtures_index.json")
        self.fixtures = read_json(fi) if os.path.exists(fi) else {"fixtures": {}, "sets": {}}
        self.values = {}      # ref -> ("one", Value|None) | ("coll", OrderedDict[sample -> Value|None])
        self.producer = {}    # (ref, sample) -> job id
        self.jobs = collections.OrderedDict()

    # ------------------------------------------------------------------ input staging
    def _value(self, t, attrs, path=None, parts=None):
        a = dict(self.ts.fixed_attributes(t))
        a.update(attrs or {})
        probe = path or next(iter((parts or {}).values()), "")
        a.setdefault("compression", _compression(probe))
        return Value(t, path=path, parts=parts, attrs=a, ts=self.ts)

    def _localize(self, path, dest_dir):
        """Local file -> absolute path. Workspace path (/owner@realm/...) -> downloaded with p3-cp."""
        if os.path.exists(path):
            return os.path.abspath(path)
        first = path.strip("/").split("/", 1)[0]
        if path.startswith("/") and "@" in first:
            os.makedirs(dest_dir, exist_ok=True)
            dest = os.path.join(dest_dir, _safe(os.path.basename(path)))
            if not os.path.exists(dest):
                self._run(["p3-cp", f"ws:{path}", dest], f"downloading {path}")
            return dest
        raise StagingError(f"input file not found: {path}")

    def _run(self, cmd, what):
        if shutil.which(cmd[0]) is None:
            raise StagingError(f"{what}: {cmd[0]} not on PATH (run inside the BV-BRC container)")
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise StagingError(f"{what} failed: {p.stderr.decode(errors='replace')[-400:]}")
        return p.stdout

    def _genome_fasta(self, gid, dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, f"{_safe(gid)}.fna")
        if not os.path.exists(dest):
            out = self._run(["p3-genome-fasta", "--contig", str(gid)], f"fetching BV-BRC genome {gid}")
            if not out.strip():
                raise StagingError(f"BV-BRC genome {gid}: no contigs returned")
            with open(dest, "wb") as f:
                f.write(out)
        return dest

    def _fixture_items(self, ref):
        """Fixture id or set name -> list of (sample_id, {'path'|'r1','r2'})."""
        fx, sets = self.fixtures.get("fixtures", {}), self.fixtures.get("sets", {})
        if ref in fx:
            return [(None, {"path": fx[ref]})]
        s = sets.get(ref)
        if s is None:
            raise StagingError(f"unknown fixture or set {ref!r} (fetch fixtures: tests/fixtures/fetch_fixtures.py)")
        if "samples" in s:
            return [(x.get("sample_id"), {"r1": x["r1"], "r2": x["r2"]}) for x in s["samples"]]
        if "members" in s:
            return [(os.path.basename(m).split(".fna")[0], {"path": m}) for m in s["members"]]
        if "r1" in s:
            return [(None, {"r1": s["r1"], "r2": s["r2"]})]
        raise StagingError(f"fixture set {ref!r} has no usable shape")

    def stage_inputs(self):
        for name, d in (self.p.get("inputs") or {}).items():
            t, src, attrs = d["type"], d.get("source") or {}, d.get("attributes") or {}
            dest = os.path.join(self.rundir, "inputs", _safe(name))
            items = []   # (sample_id, Value)
            paired = self.ts.kind(t) == "files" and "r1" in self.ts.parts(t)
            if "fixture" in src:
                for sid, it in self._fixture_items(src["fixture"]):
                    if paired:
                        items.append((sid, self._value(t, attrs, parts={"r1": it["r1"], "r2": it["r2"]})))
                    else:
                        items.append((sid, self._value(t, attrs, path=it["path"])))
            for i, lib in enumerate(src.get("paired_end_libs") or []):
                items.append((lib.get("sample_id"), self._value(t, attrs, parts={
                    "r1": self._localize(lib["read1"], dest), "r2": self._localize(lib["read2"], dest)})))
            for lib in src.get("single_end_libs") or []:
                items.append((lib.get("sample_id"), self._value(t, attrs, path=self._localize(lib["read"], dest))))
            for f in src.get("files") or []:
                items.append((None, self._value(t, attrs, path=self._localize(f, dest))))
            for f in ([src["wsid"]] if src.get("wsid") else []) + (src.get("wsids") or []):
                items.append((None, self._value(t, attrs, path=self._localize(f, dest))))
            for gid in src.get("genome_ids") or []:
                items.append((str(gid), self._value(t, attrs, path=self._genome_fasta(gid, dest))))
            unsupported = set(src) & {"srr_ids", "srr_libs", "genome_group", "feature_group", "feature_ids", "fasta_data"}
            if unsupported:
                raise StagingError(f"inputs.{name}: source {sorted(unsupported)} not supported by the runner yet")
            if not items:
                raise StagingError(f"inputs.{name}: source produced no files")
            ref = f"$inputs.{name}"
            if d.get("collection"):
                coll = collections.OrderedDict()
                for i, (sid, v) in enumerate(items, 1):
                    key = _safe(sid or f"s{i}")
                    if key in coll:
                        raise StagingError(f"inputs.{name}: duplicate sample id {key}")
                    v.label = key
                    coll[key] = v
                self.values[ref] = ("coll", coll)
            else:
                if len(items) != 1:
                    raise StagingError(f"inputs.{name}: {len(items)} items for a non-collection input "
                                       f"(set \"collection\": true to process each separately)")
                items[0][1].label = _safe(name)
                self.values[ref] = ("one", items[0][1])

    # ------------------------------------------------------------------ jobs
    def _get(self, ref, sample):
        kind, v = self.values[ref]
        if kind == "one":
            return v, self.producer.get((ref, None))
        return v.get(sample), self.producer.get((ref, sample))

    def build_jobs(self):
        steps = self.p["steps"]
        for sid in self.plan["order"]:
            st, s = self.plan["steps"][sid], steps[sid]
            m = self.mods.get(st["module"])
            scatter = st["scatter"]
            samples = list(self.values[f"$inputs.{scatter}"][1]) if scatter else [None]
            outs_coll = {oid: collections.OrderedDict() for oid in m.outputs}
            for sample in samples:
                jid = f"{sid}__{sample}" if sample else sid
                wd = os.path.join(self.rundir, "steps", sid, sample) if sample else os.path.join(self.rundir, "steps", sid)
                job = Job(jid, sid, sample, m, wd)
                inputs, input_types = {}, {}
                for pid, port in m.inputs.items():
                    raw = (s.get("in") or {}).get(pid)
                    if raw is None:
                        inputs[pid] = None
                        continue
                    many = port.get("cardinality", "one") == "many"
                    vals = []
                    for r in (raw if isinstance(raw, list) else [raw]):
                        kind, v = self.values[r]
                        if kind == "coll" and (many or not scatter):
                            for smp, x in v.items():
                                if x is not None:
                                    vals.append(x)
                                    self._dep(job, r, smp, x)
                        else:
                            x, _ = self._get(r, sample)
                            if x is not None:
                                vals.append(x)
                                self._dep(job, r, sample if kind == "coll" else None, x)
                    vals = [self._decompress_if_needed(job, port, pid, i, x) for i, x in enumerate(vals)]
                    if many:
                        inputs[pid] = vals
                    else:
                        inputs[pid] = vals[0] if vals else None
                    if vals:
                        input_types[pid] = vals[0].type
                params = st["params"]
                dbs, db_files = db_context(m, params, self.dbs,
                                           resolve=lambda e: repo_path(e["path"]) if e.get("location") == "repo_fixture"
                                           else e.get("path", ""))
                r = m.resources
                job.cpu = max(1, min(r["cpu"], self.cores))
                job.mem_gb = max(1, min(r["memory_gb"], self.mem_gb))
                rel_outputs, abs_outputs = {}, {}
                for oid, op in m.outputs.items():
                    rt = resolve_output_type(m, op, input_types, self.ts) or op["type"]
                    rel_outputs[oid] = output_value(op, rt, self.ts)
                ctx = build_context(m, inputs, rel_outputs, params, job.cpu, job.mem_gb, dbs, db_files)
                job.command = render_command(m, ctx)
                for oid, op in m.outputs.items():
                    rv = rel_outputs[oid]
                    present = eval_when(op["when"], ctx) if op.get("when") else True
                    if not present:
                        abs_outputs[oid] = None
                        continue
                    attrs = dict(self.ts.fixed_attributes(rv.type))
                    tf = op.get("type_from")
                    src_port = tf if isinstance(tf, str) else (tf or {}).get("port")
                    if src_port and isinstance(inputs.get(src_port), Value):
                        attrs = {**inputs[src_port].attrs, **attrs}
                    attrs.update(op.get("attributes") or {})
                    if rv._parts and (rv._path is None or self.ts.kind(rv.type) == "files"):
                        parts = {k: os.path.join(wd, v) for k, v in rv._parts.items()}
                        av = Value(rv.type, parts=parts, attrs=attrs, ts=self.ts)
                        paths = list(parts.values())
                    else:
                        av = Value(rv.type, path=os.path.join(wd, rv._path), attrs=attrs, ts=self.ts)
                        paths = [av._path]
                    if "compression" not in (op.get("attributes") or {}):
                        av.attrs["compression"] = _compression(paths[0])
                    av.label = sample if sample else f"{sid}.{oid}"
                    abs_outputs[oid] = av
                    if op.get("required", True):
                        job.required_outputs += paths
                job.inputs, job.outputs = inputs, abs_outputs
                self.jobs[jid] = job
                for oid, v in abs_outputs.items():
                    outs_coll[oid][sample] = v
                    self.producer[(f"{sid}.{oid}", sample)] = jid
            for oid in m.outputs:
                ref = f"{sid}.{oid}"
                if scatter:
                    self.values[ref] = ("coll", outs_coll[oid])
                else:
                    self.values[ref] = ("one", outs_coll[oid][None])
        return self.jobs

    def _dep(self, job, ref, sample, value):
        up = self.producer.get((ref, sample))
        if up:
            job.deps.add(up)
        else:  # pipeline input: an external file the executor can check for
            job.external_inputs += [value._path] if value._path else list(value._parts.values())

    def _decompress_if_needed(self, job, port, pid, i, v):
        want = (port.get("requires") or {}).get("compression")
        if want != "none" or v.attrs.get("compression") != "gzip":
            return v
        def tgt(path, tag):
            return os.path.join(job.workdir, ".modpipe", "in", f"{pid}{i}_{tag}_{os.path.basename(path)[:-3]}")
        if v._path:
            dst = tgt(v._path, "f")
            job.prelude.append(f"mkdir -p .modpipe/in && gzip -dc {shlex.quote(v._path)} > {shlex.quote(dst)}")
            nv = Value(v.type, path=dst, attrs={**v.attrs, "compression": "none"}, ts=self.ts, label=v.label)
        else:
            parts = {}
            for k, pth in v._parts.items():
                parts[k] = tgt(pth, k)
                job.prelude.append(f"mkdir -p .modpipe/in && gzip -dc {shlex.quote(pth)} > {shlex.quote(parts[k])}")
            nv = Value(v.type, parts=parts, attrs={**v.attrs, "compression": "none"}, ts=self.ts, label=v.label)
        return nv

    # ------------------------------------------------------------------ scripts
    def write(self):
        os.makedirs(os.path.join(self.rundir, ".modpipe"), exist_ok=True)
        for job in self.jobs.values():
            md = os.path.join(job.workdir, ".modpipe")
            os.makedirs(md, exist_ok=True)
            with open(os.path.join(md, "cmd.sh"), "w") as f:
                f.write("set -euo pipefail\n" + job.command + "\n")
            req = " ".join(shlex.quote(p) for p in job.required_outputs)
            prelude = "\n".join(job.prelude)
            with open(job.script, "w") as f:
                f.write(f"""#!/bin/bash
# modpipe job {job.id}: module {job.module.id} v{job.module.version}
set -uo pipefail
cd {shlex.quote(job.workdir)} || exit 1
find . -mindepth 1 -maxdepth 1 ! -name .modpipe -exec rm -rf {{}} +
rm -f .modpipe/done .modpipe/in/* 2>/dev/null
export MODPIPE_CPU={job.cpu} MODPIPE_MEM_GB={job.mem_gb:g}
# Short per-job temp dir: tools using multiprocessing put AF_UNIX sockets in $TMPDIR (path limit ~108 chars).
_tbase=${{MODPIPE_TMPDIR:-/tmp}}; [ ${{#_tbase}} -gt 40 ] && _tbase=/tmp
export TMPDIR=$(mktemp -d "$_tbase/mp.XXXXXX") || exit 1
trap 'rm -rf "$TMPDIR"' EXIT
{prelude}
TIME=/usr/bin/time; [ -x "$TIME" ] && TIMECMD=("$TIME" -v -o .modpipe/time.txt) || TIMECMD=()
"${{TIMECMD[@]}}" bash .modpipe/cmd.sh > .modpipe/stdout.txt 2> .modpipe/stderr.txt
rc=$?
if [ $rc -ne 0 ]; then
  echo "[modpipe] job {job.id} failed (exit $rc)" >&2
  echo "[modpipe] --- last stderr lines ---" >&2; tail -n 20 .modpipe/stderr.txt >&2
  echo "[modpipe] --- last stdout lines ---" >&2; tail -n 20 .modpipe/stdout.txt >&2
  grep -m 5 -iE "^(error|fatal)|error!|exception" .modpipe/stdout.txt .modpipe/stderr.txt >&2 || true
  exit $rc
fi
missing=""
for f in {req}; do [ -e "$f" ] || missing="$missing $f"; done
if [ -n "$missing" ]; then echo "[modpipe] job {job.id}: required outputs missing:$missing" >&2; exit 3; fi
rm -rf .modpipe/in
touch .modpipe/done
""")
            os.chmod(job.script, 0o755)
        with open(os.path.join(self.rundir, ".modpipe", "jobs.json"), "w") as f:
            json.dump([j.to_json() for j in self.jobs.values()], f, indent=1)


def parse_mem(s):
    return parse_memory_gb(s)
