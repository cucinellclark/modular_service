#!/usr/bin/env python3
"""P4 empirical output discovery: run one tool invocation on fixtures and record what it produces.

Runs INSIDE the BV-BRC container (python3 3.10 + PyYAML). Normally driven by submit.sh / discovery.sbatch.

Subcommands:
  count     <set.yaml>                      number of runs (array size)
  resources <set.yaml>                      "cpus mem time" for sbatch
  indices   <set.yaml> <id,id,...>          array indices for the given run ids (comma list)
  list      <set.yaml>                      index, run id, tool, mode
  run       <set.yaml> <index> [--keep-workdir]
  summarize [--results reference/tools]     build reference/tools/DISCOVERY.md from all run JSONs

Each run: create a scratch workdir, copy the input fixtures to inputs/, run `prep` (untracked setup), snapshot,
run `cmd` under /usr/bin/time -v with a timeout, then record every new/modified file (path, size, sha256,
format sniff, record counts, preview) plus runtime/RSS/exit code. The result is written to
reference/tools/<tool>/runs/<run_id>.json. The workdir is deleted unless --keep-workdir is given.
"""
import datetime
import gzip
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time

import yaml

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FIXTURE_INDEX = os.path.join(REPO, "tests", "fixtures", "data", "fixtures_index.json")
TOOL_INDEX = os.path.join(REPO, "reference", "tools", "index.json")
RESULTS = os.path.join(REPO, "reference", "tools")
HASH_MAX = 512 * 1024 * 1024        # don't hash files bigger than this
COUNT_MAX = 200 * 1024 * 1024       # don't count records in files bigger than this
TAIL = 4000                         # bytes of stdout/stderr kept


def load_set(path):
    with open(path) as f:
        s = yaml.safe_load(f)
    ids = [r["id"] for r in s["runs"]]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        sys.exit(f"duplicate run ids in {path}: {dup}")
    return s


# ---------------------------------------------------------------- output sniffing

EXT_KIND = [
    (r"\.(fastq|fq)(\.gz)?$", "fastq"), (r"\.(fasta|fa|fna|faa|ffn|fas|frn|aln|afa|mfa|xmfa|contigs)(\.gz)?$", "fasta"),
    (r"\.bam$", "bam"), (r"\.sam$", "sam"), (r"\.cram$", "cram"), (r"\.(bai|csi|crai|tbi)$", "index"),
    (r"\.vcf(\.gz)?$", "vcf"), (r"\.bcf$", "bcf"), (r"\.(gff3?|gtf)(\.gz)?$", "gff"), (r"\.(gb|gbk|gbff)$", "genbank"),
    (r"\.(nwk|newick|tree|treefile|tre|dnd)$", "newick"), (r"\.json$", "json"), (r"\.html?$", "html"),
    (r"\.(tsv|tab|txt|csv|bed|bedgraph|paf|log|out|stats?)$", "text"), (r"\.(png|svg|pdf)$", "image"),
    (r"\.(k2d|bt2l?|ht2|mmi|amb|ann|bwt|pac|sa|n..|p..|dmnd|h3[fimp]|kma.*|comp\.b|length\.b|seq\.b|name)$", "index"),
    (r"\.(tar\.gz|tgz|zip)$", "archive"),
]


def sniff(path):
    info = {}
    name = os.path.basename(path)
    kind = next((k for rx, k in EXT_KIND if re.search(rx, name, re.I)), None)
    try:
        with open(path, "rb") as f:
            head = f.read(4096)
    except OSError:
        return {"kind": "unreadable"}
    gz = head[:2] == b"\x1f\x8b"
    if gz:
        info["compressed"] = "gzip"
        try:
            with gzip.open(path, "rb") as f:
                head = f.read(4096)
        except Exception:
            head = b""
    text = bool(head) and b"\0" not in head
    if kind is None and text:
        h = head.lstrip()
        if h.startswith(b">"):
            kind = "fasta"
        elif h.startswith(b"@") and b"\n+" in head:
            kind = "fastq"
        elif h.startswith(b"##fileformat=VCF"):
            kind = "vcf"
        elif h.startswith(b"##gff-version"):
            kind = "gff"
        elif h.startswith(b"(") and head.rstrip().endswith(b";"):
            kind = "newick"
        elif h[:1] in (b"{", b"["):
            kind = "json"
        elif h[:5].lower() in (b"<!doc", b"<html"):
            kind = "html"
        else:
            kind = "text"
    if kind is None:
        kind = "binary"
    if head[:4] == b"BAM\x01":
        kind = "bam"
    info["kind"] = kind
    if text:
        lines = head.decode("utf-8", "replace").splitlines()
        info["preview"] = [l[:200] for l in lines[:3]]
    size = os.path.getsize(path)
    if text and size <= COUNT_MAX and kind in ("fasta", "fastq", "vcf", "text", "gff", "newick"):
        opener = gzip.open if gz else open
        n_lines = n_seq = n_bp = n_rec = 0
        try:
            with opener(path, "rt", errors="replace") as f:
                for i, line in enumerate(f):
                    n_lines += 1
                    if not line.startswith("#"):
                        n_rec += 1
                    if kind == "fasta":
                        if line.startswith(">"):
                            n_seq += 1
                        else:
                            n_bp += len(line.strip())
                    elif kind == "fastq" and i % 4 == 1:
                        n_seq += 1
                        n_bp += len(line.strip())
            info["lines"] = n_lines
            if kind in ("fasta", "fastq"):
                info["records"], info["residues"] = n_seq, n_bp
            elif kind in ("vcf", "gff"):
                info["records"] = n_rec
        except Exception as e:
            info["count_error"] = str(e)[:200]
    return info


def sha256(path):
    if os.path.getsize(path) > HASH_MAX:
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(root):
    snap = {}
    for dp, dn, fn in os.walk(root):
        for n in fn:
            p = os.path.join(dp, n)
            try:
                st = os.lstat(p)
            except OSError:
                continue
            snap[os.path.relpath(p, root)] = (st.st_size, st.st_mtime_ns)
    return snap


def parse_time(path):
    out = {}
    if not os.path.exists(path):
        return out
    pats = {"elapsed": r"Elapsed \(wall clock\) time.*: (.+)", "max_rss_kb": r"Maximum resident set size \(kbytes\): (\d+)",
            "cpu_pct": r"Percent of CPU this job got: (\d+)%", "exit_status": r"Exit status: (\d+)",
            "user_s": r"User time \(seconds\): ([\d.]+)", "sys_s": r"System time \(seconds\): ([\d.]+)"}
    txt = open(path, errors="replace").read()
    for k, rx in pats.items():
        m = re.search(rx, txt)
        if m:
            out[k] = m.group(1).strip()
    if "elapsed" in out:  # h:mm:ss or m:ss.ss
        parts = [float(x) for x in out["elapsed"].split(":")]
        sec = 0.0
        for p in parts:
            sec = sec * 60 + p
        out["elapsed_s"] = round(sec, 2)
    if "max_rss_kb" in out:
        out["max_rss_mb"] = round(int(out["max_rss_kb"]) / 1024, 1)
    return out


def tail(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        f.seek(0, 2)
        n = f.tell()
        f.seek(max(0, n - TAIL))
        return f.read().decode("utf-8", "replace")


def scratch_base():
    for c in (os.environ.get("MODPIPE_SCRATCH"), os.environ.get("SLURM_TMPDIR"), "/disks/tmp", "/scratch/tmp", "/tmp"):
        if c and os.path.isdir(c) and os.access(c, os.W_OK):
            return c
    return "/tmp"


def mem_gb(mem):
    m = re.match(r"(\d+)\s*([GgMm])", str(mem))
    if not m:
        return 8
    v = int(m.group(1))
    return v if m.group(2).lower() == "g" else max(1, v // 1024)


# ---------------------------------------------------------------- run

def do_run(set_path, index, keep):
    s = load_set(set_path)
    run = s["runs"][index]
    rid, tool = run["id"], run["tool"]
    res = s.get("resources", {})
    cpus = int(os.environ.get("SLURM_CPUS_PER_TASK") or res.get("cpus") or os.cpu_count())
    memg = mem_gb(res.get("mem", "8G"))
    fx = json.load(open(FIXTURE_INDEX))["fixtures"]
    tool_versions = json.load(open(TOOL_INDEX))["tools"] if os.path.exists(TOOL_INDEX) else {}

    job = os.environ.get("SLURM_ARRAY_JOB_ID") or os.environ.get("SLURM_JOB_ID") or "local"
    task = os.environ.get("SLURM_ARRAY_TASK_ID", str(index))
    wd = os.path.join(scratch_base(), os.environ.get("USER", "user"), "modpipe-discovery", s["set"], f"{rid}-{job}_{task}")
    if os.path.exists(wd):
        shutil.rmtree(wd)
    os.makedirs(os.path.join(wd, "inputs"))
    meta = os.path.join(wd, ".modpipe")
    os.makedirs(meta)

    env = dict(os.environ)
    env.update({"CPU": str(cpus), "MEM_GB": str(memg), "WORKDIR": wd, "LC_ALL": "C.UTF-8", "LANG": "C.UTF-8"})
    env["TMPDIR"] = os.path.join(wd, ".tmp")
    os.makedirs(env["TMPDIR"])
    inputs = {}
    missing = []
    for var, fid in (run.get("inputs") or {}).items():
        src = fx.get(fid)
        if not src:
            missing.append(fid)
            continue
        dst = os.path.join(wd, "inputs", os.path.basename(src.rstrip("/")))
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy(src, dst)
        env[var] = dst
        inputs[var] = {"fixture": fid, "path": os.path.relpath(dst, wd),
                       "size": os.path.getsize(dst) if os.path.isfile(dst) else None}

    result = {"schema": "modpipe/discovery-run/v1", "run_id": rid, "set": s["set"], "tool": tool,
              "mode": run.get("mode"), "description": run.get("description"),
              "tool_version": (tool_versions.get(tool) or {}).get("version"),
              "container": os.environ.get("SINGULARITY_CONTAINER") or os.environ.get("APPTAINER_CONTAINER"),
              "node": socket.gethostname(), "slurm_job": f"{job}_{task}", "cpus": cpus, "mem_gb": memg,
              "started": datetime.datetime.now().isoformat(timespec="seconds"),
              "inputs": inputs, "prep": run.get("prep"), "cmd": run["cmd"]}

    def bash(script, name, timeout, timed=False):
        script_path = os.path.join(meta, f"{name}.sh")
        with open(script_path, "w") as f:
            f.write("set -euo pipefail\n" + script)
        cmd = ["bash", script_path]
        if timed:
            cmd = ["/usr/bin/time", "-v", "-o", os.path.join(meta, "time.txt")] + cmd
        with open(os.path.join(meta, f"{name}.stdout"), "wb") as so, open(os.path.join(meta, f"{name}.stderr"), "wb") as se:
            try:
                p = subprocess.run(cmd, cwd=wd, env=env, stdout=so, stderr=se, timeout=timeout)
                return p.returncode, False
            except subprocess.TimeoutExpired:
                return None, True

    status = "ok"
    if missing:
        status = "missing_fixture"
        result["error"] = f"fixtures not fetched: {missing}"
    else:
        if run.get("prep"):
            rc, to = bash(run["prep"], "prep", run.get("prep_timeout", 3600))
            if rc != 0:
                status = "prep_failed"
                result["prep_exit"] = rc
                result["prep_stderr_tail"] = tail(os.path.join(meta, "prep.stderr"))
        if status == "ok":
            before = snapshot(wd)
            t0 = time.time()
            rc, to = bash(run["cmd"], "cmd", run.get("timeout", 7200), timed=True)
            result["wall_s"] = round(time.time() - t0, 2)
            result["exit_code"] = rc
            if to:
                status = "timeout"
            elif rc != 0:
                status = "failed"
            after = snapshot(wd)
            outs = []
            for rel, st in sorted(after.items()):
                if rel.startswith(".modpipe/") or rel.startswith(".tmp/"):
                    continue
                if before.get(rel) == st:
                    continue
                p = os.path.join(wd, rel)
                if os.path.islink(p):
                    outs.append({"path": rel, "symlink_to": os.readlink(p)})
                    continue
                o = {"path": rel, "size": st[0], "new": rel not in before}
                o.update(sniff(p))
                o["sha256"] = sha256(p)
                outs.append(o)
            result["outputs"] = outs
            result["n_outputs"] = len(outs)
            result["output_bytes"] = sum(o.get("size", 0) or 0 for o in outs)
            result["time"] = parse_time(os.path.join(meta, "time.txt"))
            result["stdout_tail"] = tail(os.path.join(meta, "cmd.stdout"))
            result["stderr_tail"] = tail(os.path.join(meta, "cmd.stderr"))
    result["status"] = status
    result["finished"] = datetime.datetime.now().isoformat(timespec="seconds")

    out_dir = os.path.join(RESULTS, tool, "runs")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{rid}.json")
    with open(out, "w") as f:
        json.dump(result, f, indent=1)
    print(f"[{status}] {rid} ({tool}) -> {os.path.relpath(out, REPO)}; outputs={result.get('n_outputs')} "
          f"wall={result.get('wall_s')}s rss={result.get('time', {}).get('max_rss_mb')}MB")
    if keep:
        print(f"workdir kept: {wd}")
    else:
        shutil.rmtree(wd, ignore_errors=True)
    return 0 if status == "ok" else 1


# ---------------------------------------------------------------- summarize

def summarize(results):
    rows = []
    for tool in sorted(os.listdir(results)):
        rdir = os.path.join(results, tool, "runs")
        if not os.path.isdir(rdir):
            continue
        for fn in sorted(os.listdir(rdir)):
            if fn.endswith(".json"):
                rows.append(json.load(open(os.path.join(rdir, fn))))
    lines = ["# P4 output discovery results", "",
             f"Generated {datetime.datetime.now().isoformat(timespec='seconds')} from `reference/tools/*/runs/*.json` "
             "(tests/discovery/run_discovery.py).", "",
             f"Runs: {len(rows)}; ok: {sum(r['status'] == 'ok' for r in rows)}; "
             f"not ok: {sum(r['status'] != 'ok' for r in rows)}", "",
             "| set | run | tool | version | status | wall s | max RSS MB | outputs | main outputs (kind) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["set"], r["run_id"])):
        outs = sorted((o for o in r.get("outputs", []) if "size" in o), key=lambda o: -o["size"])
        top = ", ".join(f"`{o['path']}` ({o.get('kind')})" for o in outs[:4])
        if len(outs) > 4:
            top += f", +{len(outs) - 4} more"
        t = r.get("time", {})
        lines.append(f"| {r['set']} | {r['run_id']} | {r['tool']} | {r.get('tool_version') or ''} | {r['status']} | "
                     f"{r.get('wall_s', '')} | {t.get('max_rss_mb', '')} | {r.get('n_outputs', '')} | {top} |")
    bad = [r for r in rows if r["status"] != "ok"]
    if bad:
        lines += ["", "## Failures", ""]
        for r in bad:
            err = (r.get("stderr_tail") or r.get("prep_stderr_tail") or r.get("error") or "").strip().splitlines()[-6:]
            lines += [f"### {r['run_id']} ({r['status']}, exit {r.get('exit_code', r.get('prep_exit'))})", "```",
                      *[l[:300] for l in err], "```", ""]
    out = os.path.join(results, "DISCOVERY.md")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {out} ({len(rows)} runs)")


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd = argv[0]
    if cmd == "count":
        print(len(load_set(argv[1])["runs"]))
    elif cmd == "resources":
        r = load_set(argv[1]).get("resources", {})
        print(r.get("cpus", 4), r.get("mem", "16G"), r.get("time", "02:00:00"))
    elif cmd == "list":
        for i, r in enumerate(load_set(argv[1])["runs"]):
            print(f"{i}\t{r['id']}\t{r['tool']}\t{r.get('mode', '')}")
    elif cmd == "indices":
        runs = load_set(argv[1])["runs"]
        want = [x for x in argv[2].split(",") if x]
        idx = {r["id"]: i for i, r in enumerate(runs)}
        bad = [w for w in want if w not in idx]
        if bad:
            sys.exit(f"unknown run ids: {bad}")
        print(",".join(str(idx[w]) for w in want))
    elif cmd == "run":
        return do_run(argv[1], int(argv[2]), "--keep-workdir" in argv)
    elif cmd == "summarize":
        summarize(argv[argv.index("--results") + 1] if "--results" in argv else RESULTS)
    else:
        sys.exit(f"unknown subcommand {cmd}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
