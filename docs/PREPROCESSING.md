# Preprocessing: Harvesting Tool Metadata

Goal: produce draft module descriptors from data instead of hand-writing ~100
of them, and make it cheap to detect when a new container image changes tools.
Everything lands in `reference/tools/<tool>/` (generated, versioned in git) and
feeds `modules/*.yaml` (curated by hand).

Steps run in rough order of cost and value.

## Status (2026-11-02)

| Step | Status | Script | Output |
|---|---|---|---|
| P1 introspection | **done** (68 tools) | `tools/harvest_tool_info.py` (in container) | `reference/tools/<id>/{version,help}.txt`, `index.json` |
| P2 BV-BRC invocations | **done** (1,253 files scanned) | `tools/mine_invocations.py` (in container) | `reference/tools/<id>/bvbrc_invocations.md`, `invocations_index.json` |
| P3 nf-core import | **done** (nf-core/modules @ b4070340) | `tools/import_nfcore.py` | `reference/tools/<id>/nfcore/<module>/{meta.yml,main.nf}`, `nfcore_index.json` |
| P4 output discovery | **done 2026-11-02**: 110 runs, 103 ok, 7 documented failures | `tests/discovery/` (Slurm job arrays per set) | `reference/tools/<id>/runs/<run_id>.json`, `reference/tools/DISCOVERY.md` |
| P5 fixtures | **done** | `tests/fixtures/fetch_fixtures.py` | `tests/fixtures/data/` |
| P6 database registry | **done 2026-11-03**: 35 entries (9 verified, 24 unverified, 2 missing) | — | `resources/databases.yaml` |
| P7 type mapping | **done 2026-11-03**: 125 types, 54 formats, 16 converters | `tools/check_types.py` | `types/types.yaml`, `types/wstypes.yaml`, `reference/types_coverage.md` |

Combined table: [`reference/tools/SUMMARY.md`](../reference/tools/SUMMARY.md)
(`tools/build_tool_summary.py`). The tool list and per-tool overrides
(custom version/help commands, aliases, nf-core mapping) are in
`tools/tool_list.json`.

Re-run everything after a container update:
```bash
S=/vol/patric3/production/containers/ubuntu-176-build12-2.sif
singularity exec $S python3 tools/harvest_tool_info.py tools/tool_list.json reference/tools
singularity exec $S python3 tools/mine_invocations.py  tools/tool_list.json reference/tools
python3 tools/import_nfcore.py <nf-core clone> tools/tool_list.json reference/tools
python3 tools/build_tool_summary.py tools/tool_list.json reference/tools
git diff reference/tools/index.json      # version drift
```

### Findings from P1–P3
- **diamond and antiSMASH crash on the dev host** ("Illegal instruction" /
  core dump). They are probably built for a newer CPU instruction set. Check
  them on compute nodes before writing modules for them.
- antiSMASH is **not on PATH**; it lives in its own venv at
  `runtime/antismash-7-1-0-1/bin/antismash`.
- `samtools` and `bcftools` on PATH are the **1.13** distro builds, although
  the runtime also contains `samtools-1.20` and `bcftools-1.17`. Decide which
  one modules pin.
- `mmseqs version` prints `17`, but the runtime directory is
  `mmseqs2-13-45111`. Confirm which binary is used.
- Gblocks is interactive with no help flag; its module needs an adapter.
- nf-core has no module for: IRMA, glimmer3, vigor4, clustalw,
  progressiveMauve, Gblocks, kSNP4, primer3, minced. Their port definitions
  come from P2/P4 only.
- Tools with no BV-BRC usage (only P1/P3 to go on): bbduk, fastplong, minced,
  Gblocks, raxml-ng, iqtree2, parsnp, antiSMASH. Check these more carefully.
- nf-core `meta.yml` gives output **file patterns + EDAM terms** per output
  channel. This is the best starting point for our output ports and type
  vocabulary (P7).

### Findings from P4 (110 runs on Slurm `compute`, 2026-11-02)
Results: `reference/tools/DISCOVERY.md` and `reference/tools/<tool>/runs/*.json`.

Container problems that modules must work around (or that need a container fix):
- **bracken** wrapper is broken (it looks for `bin/src/est_abundance.py`); call
  `est_abundance.py` directly, as BV-BRC does.
- **freyja demix**: the container python lacks `pyarrow`, so the `.feather` barcodes
  fail; freyja's bundled `data/curated_lineages.json` is missing. Works with
  CSV barcodes plus `--meta curated_lineages.json --lineageyml lineages.yml` from
  `application-backend/bvbrc_taxonomic_classification_2/data/`.
- **pangolin**: the scorpio step fails; `--skip-scorpio` works (pangolin-data 1.30).
  The BV-BRC invocation doesn't skip it; worth checking whether production
  output has the same problem.
- **parsnp** can't run: `harvesttools` is not in the container.
- **antiSMASH** starts on compute nodes (no crash), but its databases are not
  installed.
- **bbduk** `ref=adapters` resource is missing from the Debian bbmap.jar, so supply
  an adapter FASTA.
- **FastTreeMP is 2.1.3; FastTree is 2.1.11**. Only the latter supports `-lg`.
  Modules should pin one of them deliberately.
- **samtools on PATH (1.13) has no `consensus`**; runtime `samtools-1.20` works.
- **diamond works on compute nodes**; its crash is specific to the dev host.

Spec lessons: kSNP rejects input file names with extra dots; snpEff 4.3t does
not support `-noCheckCds`/`-noCheckProtein`; flye cannot assemble the ~540 bp
SARS-CoV-2 ONT reads (a data limitation).

Resource notes: geNomad end-to-end peaks at **~18.7 GB RSS** even on a 30 kb genome
(database load), and took 9 min. canu writes ~380 files (mostly intermediates),
SPAdes ~100–125. These are the cases where curated output ports matter most.

## P1. Tool introspection snapshot (cheap, fully automatic)

For every candidate binary in TOOL_INVENTORY, inside the container:
- resolved path, `--version` output, `--help` / `-h` output (with a timeout;
  some tools print help to stderr or exit non-zero)
- container image path and checksum/mtime

Output: `reference/tools/<tool>/{version.txt,help.txt}` plus `reference/tools/index.json`.

Uses: parameter lists for descriptors (help text can be parsed or
LLM-assisted into draft `parameters:`), and **drift detection**: re-run on each
new container image and diff the versions and help text.

## P2. Mine existing BV-BRC invocations (cheap, semi-automatic)

Extract the actual command lines (flags, defaults, pre/post-processing) for each
tool from `plbin/App-*.pl`, `pybin/`, `lib/Bio/P3/`, `workflows/*/snakefile`.
These are tested in production and are the best default parameter sets.
Output: `reference/tools/<tool>/bvbrc_invocations.md` (file:line + snippet).

## P3. Import community I/O declarations (cheap, needs network)

- **nf-core modules** (`modules/nf-core/<tool>/<subcmd>/meta.yml`): declares
  inputs/outputs with file patterns and **EDAM ontology** format/data terms,
  per tool *sub-command* (e.g. `samtools/sort`, `samtools/index`). Highest
  value: it gives output patterns and types directly.
- **snakemake-wrappers**: input/output names and example rules.
- **bio.tools / EDAM**: consider EDAM terms as the backbone (or at least a
  cross-reference) of our type vocabulary (`format_1930` = FASTQ, etc.) so
  types are not ad hoc.

Output: `reference/tools/<tool>/nfcore_meta.yml`. Caveat: versions may differ
from the container's, so P4 is the source of truth.

## P4. Empirical output discovery (most expensive, most reliable)

Implemented as Slurm job arrays (one per resource class / tool group): see
[tests/discovery/README.md](../tests/discovery/README.md).


This is the "all possible output files" step. For each tool, run it inside the
container on **tiny fixtures** across a small **mode matrix** (paired vs single,
dna vs protein, `--meta` vs `--isolate`, etc.), and record:
- the full output file tree (path, size, detected format via extension/sniffing)
- runtime, peak memory (`/usr/bin/time -v`), threads used
- exit code and stderr tail

Output: `reference/tools/<tool>/runs/<mode>/manifest.json`.

Uses:
- Fill descriptor `outputs:` with **curated** ports. Most tools write many
  files (logs, intermediates, `K21/`… for SPAdes). We expose the
  meaningful ones as typed ports and keep the full manifest only as reference.
  This also tells us which outputs are **conditional** on parameters.
- Seed `resources:` defaults from measured runtime and memory (scaled).
- These runs become the per-module **smoke tests** in CI.

Requires a fixtures set (P5).

## P5. Test fixtures

Research done; see [TEST_DATA.md](TEST_DATA.md).


Small, fast, redistributable data, e.g.:
- short reads: ~50k read-pair subsample of a small bacterial isolate; SE variant
- long reads: small ONT subsample
- a phage or small viral genome (contigs), a GenBank file, a GTO
- ~20 homologous proteins / genes (for MSA → tree)
- a VCF / BAM generated from the above (or produced by upstream modules)

Store under `tests/fixtures/` (or on `/vol` if too big for git).

## P6. Reference database inventory

**Lead (2026-11-02):** `p3x-run-qa.pl` binds
`/vol/patric3/production/data-images/patric-data-2022-0119:/opt/patric-common/data`,
`/vol/blastdb/bvbrc-service`, and `/vol/patric3/metagenome_dbs` into the container.
Start the inventory there.


kraken2 DBs, BLAST DBs, host genomes (hostile), AMRFinder DB, geNomad DB,
CheckV DB, chewBBACA schemas, freyja barcodes. These are not visible at
`/opt/patric-common/data` in a bare `singularity exec`, so they are probably
bind-mounted at job runtime. Find the bind mounts used by the scheduler (Slurm
batch template in app_service: `slurm_batch.tt`) and record DB id → path →
version in `resources/databases.yaml`.

## P7. Type mapping table

Join the EDAM formats (P3), observed output formats (P4), and BV-BRC workspace
types (app specs + Workspace module type list) into `types/types.yaml` and
`types/wstypes.yaml`.

## Suggested order

P1 + P2 now (an afternoon, no external dependencies), then P3 (needs network
approval), then P5 + P4 for the ~15 tools used by the first curated
pipelines, then the rest incrementally. P6 runs in parallel; it blocks any
module that needs a DB.
