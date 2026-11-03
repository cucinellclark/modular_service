#!/usr/bin/env python3
"""P2: mine existing BV-BRC invocations of each tool. Run INSIDE the container:

    singularity exec $SIF python3 tools/mine_invocations.py tools/tool_list.json reference/tools

Scans BV-BRC code under /opt/p3/deployment (plbin, pybin, lib, workflows, services) for places
where a tool binary is referenced in an invocation-like context, and writes
<out>/<id>/bvbrc_invocations.md (merged context hunks with file:line) plus <out>/invocations_index.json.
"""
import json, os, re, sys

ROOT = "/opt/p3/deployment"
SCAN_DIRS = ["plbin", "pybin", "lib", "workflows", "services"]
TEXT_EXT = {".pl", ".pm", ".py", ".sh", ".tt", ".smk", ".R", ".r", ".json", ".yaml", ".yml", ""}
SKIP_PARTS = {"__pycache__", "site-packages", "node_modules", ".git", "app_specs", "webroot", "test_data", "t"}
MAX_FILE = 2_000_000
BEFORE, AFTER = 6, 12
MAX_HUNKS = 25

# Extra names a tool may be invoked by (besides its binary).
ALIASES = {
    "spades": ["spades.py", "metaspades.py", "rnaviralspades.py"],
    "quast": ["quast.py", "metaquast.py", "quast-lg.py"],
    "blastn": ["blastn", "makeblastdb", "blastx", "tblastn"],
    "chewbbaca": ["chewBBACA.py", "chewBBACA"],
    "fasttree": ["FastTree", "FastTreeMP", "fasttree"],
    "raxmlhpc": ["raxmlHPC", "raxmlHPC-PTHREADS", "raxmlHPC-PTHREADS-SSE3", "raxmlHPC-PTHREADS-AVX"],
    "krona": ["ktImportText", "ktImportTaxonomy"],
    "bracken": ["bracken", "est_abundance.py"],
    "mafft": ["mafft", "mafft-linsi", "mafft-einsi", "mafft-ginsi"],
    "hmmscan": ["hmmscan", "hmmsearch", "hmmbuild"],
    "trnascan": ["tRNAscan-SE"],
    "snpeff": ["snpEff", "snpEff.sh"],
    "bbduk": ["bbduk.sh"], "bbnorm": ["bbnorm.sh"],
    "irma": ["IRMA"], "ksnp4": ["kSNP4", "kSNP3"],
    "primer3": ["primer3_core"],
    "progressivemauve": ["progressiveMauve"],
    "htseq-count": ["htseq-count"],
}


def is_text_candidate(path):
    ext = os.path.splitext(path)[1]
    return ext in TEXT_EXT or "snakefile" in path.lower() or "Snakefile" in path


def iter_files():
    for d in SCAN_DIRS:
        base = os.path.join(ROOT, d)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [x for x in dirnames if x not in SKIP_PARTS]
            for fn in filenames:
                p = os.path.join(dirpath, fn)
                if not is_text_candidate(p):
                    continue
                try:
                    if os.path.getsize(p) > MAX_FILE or os.path.islink(p):
                        continue
                    with open(p, "rb") as f:
                        data = f.read()
                except OSError:
                    continue
                if b"\0" in data[:4096]:
                    continue
                yield p, data.decode("utf-8", "replace").splitlines()


def tool_regex(names):
    # Name used as a command: preceded by start/quote/space/slash/paren/bracket/comma, not '$' '@' '_' '-' or word char,
    # followed by quote/space/end/paren/comma/semicolon. Avoids matching variables like $mlst or module names.
    alt = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
    return re.compile(r"(?:^|(?<=[\s\"'`/(\[,=]))(?:%s)(?=$|[\s\"'`),;\]])" % alt)


INVOKE_HINT = re.compile(r"system|run\(|IPC::Run|subprocess|Popen|check_call|check_output|shell:|cmd|command|"
                         r"exec|qx|`|\[\s*[\"']|push\s*\(\s*@", re.I)


def main(tool_list, outdir):
    tools = json.load(open(tool_list))["tools"]
    regs = {}
    for t in tools:
        names = set(ALIASES.get(t["id"], [])) | {t["binary"]}
        regs[t["id"]] = tool_regex(names)
    hits = {t["id"]: {} for t in tools}  # id -> file -> [line_idx]
    nfiles = 0
    files_cache = {}
    for path, lines in iter_files():
        nfiles += 1
        for i, line in enumerate(lines):
            s = line.strip()
            if not s or len(s) > 600:
                continue
            for tid, rx in regs.items():
                if rx.search(line):
                    hits[tid].setdefault(path, []).append(i)
                    files_cache[path] = lines
    index = {"root": ROOT, "files_scanned": nfiles, "tools": {}}
    for t in tools:
        tid = t["id"]
        per_file = hits[tid]
        d = os.path.join(outdir, tid)
        os.makedirs(d, exist_ok=True)
        hunks = []
        for path, idxs in per_file.items():
            lines = files_cache[path]
            # merge overlapping windows
            cur = None
            for i in sorted(set(idxs)):
                lo, hi = max(0, i - BEFORE), min(len(lines), i + AFTER + 1)
                if cur and lo <= cur[1]:
                    cur[1] = max(cur[1], hi); cur[2].append(i)
                else:
                    if cur: hunks.append((path, *cur))
                    cur = [lo, hi, [i]]
            if cur: hunks.append((path, *cur))

        # rank hunks: invocation-looking first, then services (plbin/pybin/workflows) before lib
        def score(h):
            path, lo, hi, idxs = h
            lines = files_cache[path]
            inv = sum(1 for i in range(lo, hi) if INVOKE_HINT.search(lines[i]))
            loc = 0 if "/plbin/" in path or "/pybin/" in path or "/workflows/" in path else 1
            return (-min(inv, 5), loc, path, lo)
        hunks.sort(key=score)
        rel_files = sorted({os.path.relpath(h[0], ROOT) for h in hunks})
        index["tools"][tid] = {"files": rel_files, "hunks": len(hunks)}
        with open(os.path.join(d, "bvbrc_invocations.md"), "w") as f:
            f.write(f"# BV-BRC invocations of `{t['binary']}` ({tid})\n\n")
            f.write(f"Auto-mined from `{ROOT}` by tools/mine_invocations.py. "
                    f"{len(hunks)} hunk(s) in {len(rel_files)} file(s)"
                    + (f"; showing top {MAX_HUNKS}" if len(hunks) > MAX_HUNKS else "") + ".\n"
                    "Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.\n\n")
            if not hunks:
                f.write("_No references found. Tool may be unused by BV-BRC services or invoked indirectly._\n")
            f.write("Files:\n" + "".join(f"- `{r}`\n" for r in rel_files) + "\n")
            for path, lo, hi, idxs in hunks[:MAX_HUNKS]:
                lines = files_cache[path]
                rel = os.path.relpath(path, ROOT)
                f.write(f"## `{rel}:{idxs[0] + 1}`\n\n```\n")
                for i in range(lo, hi):
                    mark = ">>" if i in idxs else "  "
                    f.write(f"{mark}{i + 1:5d}  {lines[i]}\n")
                f.write("```\n\n")
        print(f"{tid:18s} {len(hunks):4d} hunks  {len(rel_files):3d} files", flush=True)
    with open(os.path.join(outdir, "invocations_index.json"), "w") as f:
        json.dump(index, f, indent=1, sort_keys=True)
    print(f"scanned {nfiles} files", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
