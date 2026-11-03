#!/usr/bin/env python3
"""Fetch ModularService test fixtures listed in manifest.json.

Standard library only (Python >= 3.8). Runs on the host or inside the BV-BRC container.

Examples:
    python3 tests/fixtures/fetch_fixtures.py --list
    python3 tests/fixtures/fetch_fixtures.py                    # tiers T0,T1
    python3 tests/fixtures/fetch_fixtures.py --tier T0
    python3 tests/fixtures/fetch_fixtures.py --only portiera_hybrid,sarscov2_genome
    python3 tests/fixtures/fetch_fixtures.py --container /vol/patric3/production/containers/ubuntu-176-build12-2.sif
    python3 tests/fixtures/fetch_fixtures.py --update-checksums  # record sha256 of fetched files in the manifest

Sources:
  nfcore        nf-core/test-datasets, pinned to a commit; sha256 verified strictly.
  bvbrc_genome  `p3-genome-fasta --contig <id>` (BV-BRC CLI on PATH, or via --container).
                BV-BRC data can change over time, so a checksum mismatch is only a warning.

Outputs, under --dest (default tests/fixtures/data, which is gitignored):
  <dest>/<fixture dest path>      the files (tarballs with "unpack" are also extracted next to themselves)
  <dest>/fixtures_index.json      fixture id -> absolute path, plus resolved sets (for tests/pipelines)
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MANIFEST = os.path.join(HERE, "manifest.json")
DEFAULT_DEST = os.path.join(HERE, "data")
RETRIES = 3


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, out):
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "modpipe-fetch-fixtures"})
            with urllib.request.urlopen(req, timeout=120) as r, open(out, "wb") as f:
                shutil.copyfileobj(r, f)
            return
        except Exception as e:  # network errors, HTTP errors
            last = e
            time.sleep(2 * attempt)
    raise RuntimeError(f"download failed after {RETRIES} attempts: {url}: {last}")


def run_bvbrc(cmd, out, container):
    if shutil.which(cmd[0]):
        full = cmd
    elif container:
        full = ["singularity", "exec", container] + cmd
    else:
        raise RuntimeError(f"{cmd[0]} not on PATH; run inside the container or pass --container SIF")
    with open(out, "wb") as f:
        p = subprocess.run(full, stdout=f, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError(f"{' '.join(full)} failed (rc={p.returncode}): {p.stderr.decode(errors='replace')[-500:]}")
    if os.path.getsize(out) == 0:
        raise RuntimeError(f"{' '.join(full)} produced no output")


def safe_extract(tar_path, dest_dir):
    """Extract regular files/dirs only; refuse absolute paths, '..', and links."""
    with tarfile.open(tar_path) as t:
        members = []
        for m in t.getmembers():
            name = os.path.normpath(m.name)
            if os.path.isabs(name) or name.startswith(".."):
                raise RuntimeError(f"unsafe path in {tar_path}: {m.name}")
            if not (m.isfile() or m.isdir()):
                continue  # skip symlinks, hardlinks, devices
            members.append(m)
        # If the archive already wraps everything in a top-level dir named like dest_dir
        # (e.g. kraken2.tar.gz -> kraken2/...), extract into the parent to avoid kraken2/kraken2/.
        tops = {os.path.normpath(m.name).split(os.sep)[0] for m in members}
        target = dest_dir
        if tops == {os.path.basename(dest_dir)}:
            target = os.path.dirname(dest_dir)
        os.makedirs(target, exist_ok=True)
        for m in members:
            t.extract(m, target)


def unpack_dir(path):
    for ext in (".tar.gz", ".tgz", ".tar"):
        if path.endswith(ext):
            return path[: -len(ext)]
    return path + ".d"


def select(manifest, tiers, only):
    fixtures = manifest["fixtures"]
    if only:
        wanted = set()
        sets = manifest.get("sets", {})
        for name in only:
            if name in sets:
                wanted |= set(set_members(sets[name]))
            else:
                wanted.add(name)
        known = {f["id"] for f in fixtures}
        unknown = wanted - known
        if unknown:
            sys.exit(f"unknown fixture/set id(s): {', '.join(sorted(unknown))}")
        return [f for f in fixtures if f["id"] in wanted]
    return [f for f in fixtures if f["tier"] in tiers]


def set_members(s):
    """All fixture ids referenced anywhere in a set definition."""
    out = []

    def walk(x, key=None):
        if isinstance(x, dict):
            for k, v in x.items():
                if k not in ("type", "note", "sample_id", "bvbrc_reference_genome_id"):
                    walk(v, k)
        elif isinstance(x, list):
            for v in x:
                walk(v, key)
        elif isinstance(x, str):
            out.append(x)

    walk(s)
    return out


def resolve_set(s, paths):
    if isinstance(s, dict):
        return {k: (v if k in ("type", "note", "sample_id", "bvbrc_reference_genome_id") else resolve_set(v, paths))
                for k, v in s.items()}
    if isinstance(s, list):
        return [resolve_set(v, paths) for v in s]
    if isinstance(s, str):
        return paths.get(s)  # None if that fixture was not fetched
    return s


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default=DEFAULT_MANIFEST)
    ap.add_argument("--dest", default=DEFAULT_DEST)
    ap.add_argument("--tier", default="T0,T1", help="comma-separated tiers (default T0,T1)")
    ap.add_argument("--only", default="", help="comma-separated fixture ids and/or set names")
    ap.add_argument("--container", default=os.environ.get("MODPIPE_SIF"),
                    help="Singularity image used for bvbrc_genome fixtures when p3 CLI is not on PATH")
    ap.add_argument("--skip-bvbrc", action="store_true", help="skip bvbrc_genome fixtures")
    ap.add_argument("--force", action="store_true", help="re-fetch even if present and valid")
    ap.add_argument("--update-checksums", action="store_true", help="write sha256 of fetched files into the manifest")
    ap.add_argument("--list", action="store_true", help="list fixtures and sets, then exit")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    manifest = json.load(open(a.manifest))
    tiers = {t.strip() for t in a.tier.split(",") if t.strip()}
    only = [x.strip() for x in a.only.split(",") if x.strip()]

    if a.list:
        for f in manifest["fixtures"]:
            size = f"{f['size'] / 1e6:7.2f}M" if f.get("size") is not None else "      ?"
            print(f"{f['tier']}  {size}  {f['id']:32s} {f['type']:28s} {f.get('organism', '')}")
        print("\nsets:", ", ".join(manifest.get("sets", {})))
        return 0

    todo = select(manifest, tiers, only)
    if a.skip_bvbrc:
        todo = [f for f in todo if f["source"] != "bvbrc_genome"]
    dest = os.path.abspath(a.dest)
    src = manifest["sources"]
    failures, fetched, skipped, updated = [], 0, 0, 0

    for f in todo:
        out = os.path.join(dest, f["dest"])
        strict = f["source"] == "nfcore"
        if os.path.exists(out) and not a.force:
            if not f.get("sha256") or sha256_file(out) == f["sha256"]:
                skipped += 1
                if f.get("unpack") and not os.path.isdir(unpack_dir(out)) and not a.dry_run:
                    safe_extract(out, unpack_dir(out))
                continue
            print(f"[stale] {f['id']}: checksum differs, re-fetching")
        if f["source"] == "nfcore":
            what = src["nfcore"]["url"].format(commit=src["nfcore"]["commit"], path=f["path"])
        elif f["source"] == "bvbrc_genome":
            what = " ".join(c.format(genome_id=f["genome_id"]) for c in src["bvbrc_genome"]["command"])
        else:
            failures.append((f["id"], f"unknown source {f['source']}"))
            continue
        print(f"[fetch] {f['id']:32s} <- {what}")
        if a.dry_run:
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(out), suffix=".part")
        os.close(fd)
        try:
            if f["source"] == "nfcore":
                download(what, tmp)
            else:
                cmd = [c.format(genome_id=f["genome_id"]) for c in src["bvbrc_genome"]["command"]]
                run_bvbrc(cmd, tmp, a.container)
            digest = sha256_file(tmp)
            if f.get("sha256") and digest != f["sha256"]:
                msg = f"sha256 mismatch (expected {f['sha256'][:12]}..., got {digest[:12]}...)"
                if strict:
                    raise RuntimeError(msg)
                print(f"[warn]  {f['id']}: {msg}; BV-BRC data may have changed")
            os.replace(tmp, out)
            if f.get("unpack"):
                d = unpack_dir(out)
                if os.path.isdir(d):
                    shutil.rmtree(d)
                safe_extract(out, d)
            if a.update_checksums and f.get("sha256") != digest:
                f["sha256"] = digest
                updated += 1
            fetched += 1
        except Exception as e:
            failures.append((f["id"], str(e)))
            if os.path.exists(tmp):
                os.remove(tmp)

    if a.update_checksums and not a.dry_run:
        # also record checksums for files that were already present
        for f in todo:
            out = os.path.join(dest, f["dest"])
            if not f.get("sha256") and os.path.exists(out):
                f["sha256"] = sha256_file(out)
                updated += 1
        if updated:
            with open(a.manifest, "w") as fh:
                json.dump(manifest, fh, indent=1)
                fh.write("\n")

    if not a.dry_run:
        # index of everything present on disk (not just this run's selection)
        paths = {}
        for f in manifest["fixtures"]:
            out = os.path.join(dest, f["dest"])
            if os.path.exists(out):
                paths[f["id"]] = out
                if f.get("unpack") and os.path.isdir(unpack_dir(out)):
                    paths[f["id"] + ":dir"] = unpack_dir(out)
        index = {"manifest": os.path.abspath(a.manifest), "dest": dest, "fixtures": paths,
                 "sets": {k: resolve_set(v, paths) for k, v in manifest.get("sets", {}).items()}}
        os.makedirs(dest, exist_ok=True)
        with open(os.path.join(dest, "fixtures_index.json"), "w") as fh:
            json.dump(index, fh, indent=1)

    print(f"\nfetched {fetched}, already present {skipped}, checksums updated {updated}, failed {len(failures)}")
    for fid, err in failures:
        print(f"  FAILED {fid}: {err}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
