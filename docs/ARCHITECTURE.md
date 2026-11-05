# Modular Service: Proposed Architecture (draft)

Status: draft for discussion. Choices still open are marked **OPEN**; see also
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

## 0. Goals

1. Know every available tool, with typed inputs and outputs.
2. Let users and developers connect tools into pipelines, but **only where the
   types are compatible**, and validate the result before anything runs.
3. Make adding a new tool a **single self-contained descriptor** (plus an
   optional small Python adapter), with no engine changes.
4. Run inside the existing container and the AppService/Slurm machinery, so
   the result is one normal BV-BRC job: `App-ModularPipeline`.

## 1. Components

```
                    ┌────────────────────────────────────────────┐
  UI / CLI / API ──▶│  ModularPipeline app spec (pipeline JSON)  │
                    └───────────────┬────────────────────────────┘
                                    ▼
  App-ModularPipeline.pl   (Perl, AppScript)                      ← "shell"
    preflight: call python `modpipe plan --preflight` → cpu/mem/runtime
    run:       stage inputs from workspace (ReadSet, ws download)
               call python `modpipe run config.json`
               upload outputs (p3-cp + suffix→wstype map)
                                    ▼
  modpipe  (Python package)                                       ← "core"
    registry/   load + validate module descriptors (modules/*.yaml)
    types/      data-type hierarchy + compatibility rules
    pipeline/   parse pipeline JSON → DAG, type-check edges, resolve params
    executors/  local | snakemake | appservice   (pluggable, see §4)
    adapters/   optional per-module Python hooks (build cmd, collect outputs)
```

Layout mirrors `App-TaxonomicClassification.pl` + `workflows/bvbrc_*`, which
already use this split.

**Prototype UI path (built 2026-11-03).** Until the app is registered with the production app service, a small
HTTP API in the core (`lib/modpipe/api.py`, `bin/modpipe serve`) serves the BV-BRC-Web page and submits jobs
itself:

```
  BV-BRC-Web /app/ModularPipeline  (Template form | Graph editor | JSON)   ← docs/UI.md
        │  GET /api/templates, /api/catalog, /api/source_options; POST /api/validate (live, debounced)
        ▼
  modpipe API (Python)  ── POST /api/submit ──▶ sbatch tests/app/run_app.sbatch ──▶ App-ModularPipeline.pl
```

## 2. Data type system

**Defined in [`types/types.yaml`](../types/types.yaml)** (125 types, 54 formats). Workspace mapping is in
[`types/wstypes.yaml`](../types/wstypes.yaml) and installed reference data in
[`resources/databases.yaml`](../resources/databases.yaml). Validate with `python3 tools/check_types.py`.
Decisions (2026-11-03):

- **Names**: our own dotted hierarchy (`reads.short.paired`, `sequences.dna.contigs`,
  `alignment.reads.bam`, `table.tsv.amr`, `annotation.gto`). EDAM format/data ids are attached as
  cross-references; nf-core tags only cover file formats.
- **Compatibility**: an output may feed an input if its type equals the input type or is a descendant of it
  (dotted prefix), and its attributes satisfy the input's `requires`. Abstract types appear only on inputs.
  Near-miss edges can be fixed by listed **converters**, which are ordinary modules (e.g. sam->bam,
  gto->genbank via `rast-export-genome`).
- **Compression is an attribute** (`compression: none|gzip|bgzip`), not a type. The engine (de)compresses
  as needed.
- **Kinds**: `file`, `files` (named parts, e.g. paired reads `r1`/`r2`, BAM + index), `prefix`
  (BLAST/bwa index file sets), `directory`, `value` (BV-BRC genome ids, groups, SRA accessions; resolved at
  staging time).
- **Databases**: installed reference data is chosen by registry id as a module **parameter**
  (registry-only types such as `database.genomad`). Databases and indexes built inside a pipeline
  (`database.blast.prot`, `index.bwa`, ...) flow as **ports**.
- **GTO** (`annotation.gto`) is in the vocabulary; RASTtk step modules that read and write it are **deferred**.
- **Workspace**: always save with an explicit, specific workspace type (`save:` table). Accept inputs by
  workspace type plus content sniffing, because production storage is inconsistent: FASTA saved as
  `reads`, BAMs as `unspecified`, alignments as `txt`. See `quirks:` in `wstypes.yaml`.
- Coverage check: 81% of top-level files produced in the P4 discovery runs match a defined format
  ([`reference/types_coverage.md`](../reference/types_coverage.md)). Most of the rest are tool intermediates
  or fixed-name files that descriptors map explicitly.

## 3. Module descriptor

> **Implemented**: the authoritative schema is [MODULE_SCHEMA.md](MODULE_SCHEMA.md), enforced by `bin/modpipe lint`.
> The example below is the original draft, kept for context.

One YAML file per tool module in `modules/`. Example: [`modules/fastp.yaml`](../modules/fastp.yaml).

```yaml
id: fastp
version: 1                      # descriptor version (bump on breaking change)
tool: {name: fastp, binary: fastp, version_cmd: "fastp --version"}
category: read_qc
label: "fastp read trimming & QC"
description: "Adapter/quality trimming with QC report."
inputs:
  - id: reads
    type: reads.short           # accepts .paired or .single
    required: true
outputs:
  - id: trimmed_reads
    type: reads.short           # same pairedness as input  → `type_from: reads`
    type_from: reads
    path: "trimmed/{sample}{_R1,_R2}.fastq.gz"
  - id: qc_report
    type: report.html
    path: "fastp.html"
  - id: qc_json
    type: report.json
    path: "fastp.json"
parameters:                      # same vocabulary as BV-BRC app specs
  - {id: qualified_quality_phred, type: int, default: 15, min: 0, max: 60}
  - {id: length_required, type: int, default: 50}
  - {id: detect_adapter_for_pe, type: bool, default: true}
resources:                       # used by preflight aggregation
  cpu: 4
  memory: 8G
  runtime: "1h + 10m per GB input"    # simple expression language, OPEN
command: >-                      # Jinja-style template; or `adapter: fastp.py`
  fastp -w {{cpu}}
  {% if inputs.reads.paired %} -i {{inputs.reads.r1}} -I {{inputs.reads.r2}}
     -o {{outputs.trimmed_reads.r1}} -O {{outputs.trimmed_reads.r2}}
  {% else %} -i {{inputs.reads.r1}} -o {{outputs.trimmed_reads.r1}} {% endif %}
  -q {{params.qualified_quality_phred}} -l {{params.length_required}}
  -h {{outputs.qc_report}} -j {{outputs.qc_json}}
provenance:
  derived_from: "reference_guided_assembly.py / run_viral_assembly.py"
```

For tools whose invocation doesn't fit a template (multi-step, output
discovery, recipe logic like `p3x-assembly.py`), the descriptor names a
Python **adapter** class implementing `build_commands()` and
`collect_outputs()`. Templates are for simple cases; adapters cover the rest.

## 4. Execution backend: generated Snakemake (DECIDED 2026-11-02)

> **Implemented 2026-11-03** (`lib/modpipe/materialize.py`, `executors.py`, `run.py`; `bin/modpipe run`).
> The materializer expands the validated pipeline into concrete jobs (one per step, or one per step x sample
> when scattering), stages inputs, renders commands and writes a wrapper `job.sh` per job. That wrapper cleans
> the job dir, decompresses inputs for ports that require `compression: none`, runs the command under
> `/usr/bin/time -v` and checks required outputs. Executors only schedule those scripts:
> - **snakemake**: one rule per job. Dependencies go through `.modpipe/done` markers, because Snakemake
>   can't use undeclared outputs as inputs. Rules get `threads` and `resources: mem_mb`.
> - **local**: a small CPU/memory-budgeted parallel scheduler for dev and tests.
> Every run writes `outputs/` (+ `manifest.json` with types and workspace types) and `pipeline_run.json`
> (provenance). Verified on compute nodes with three test pipelines (tests/e2e/).

The engine produces a validated DAG; an **executor** turns it into work.
The executor interface stays pluggable, but the production backend is
**Snakemake codegen**, with a minimal **local runner** kept for unit tests and
debugging. Whole services as nodes (child App jobs) are **out of scope**.

> **2026-11-05: second execution path, per tool through GoWe.** `App-ModularStep` runs one module per BV-BRC job;
> GoWe chains them (one CWL tool per module), passing data between steps as workspace output folders tagged with
> modpipe metadata (docs/SERVICE.md). Validation stays here; GoWe only schedules. `ModularPipeline` (this
> section's one-job Snakemake path) stays for whole pipelines.

How it works: the engine emits one Snakemake rule per (step, sample) shape,
plus a `config.json`, then runs
`snakemake --cores $P3_ALLOCATED_CPU --resources mem_mb=...` inside the job.
Per-rule `threads:` and `resources:` come from the module descriptors.

### Why Snakemake over Nextflow

| | Snakemake | Nextflow |
|---|---|---|
| In container today | **Yes**, 7.32.4 | No (Java 11 present, nextflow missing) |
| Used by BV-BRC already | Yes (4 services: TaxonomicClassification, Wastewater, cgMLST, WG-SNP) | No |
| Language fit | Python, so the core can generate and introspect it natively | Groovy DSL, a second language to maintain |
| DAG model | File-based, which matches our `path`-declared output ports | Channel dataflow: more elegant for streaming and scatter |
| Scatter/gather | Wildcards + `expand()`; `checkpoint` for data-dependent fan-out | Native and nicer |
| Containers per step | Supported, but we don't need it (one image) | Its main strength; not needed here |
| Ecosystem | snakemake-wrappers | **nf-core modules**, ~1,400 tools with `meta.yml` I/O declarations |

Nextflow would only clearly win if we needed per-step containers or cloud
executors. Its best asset for us, the nf-core module catalog, can be mined
for I/O metadata **without running Nextflow** (see PREPROCESSING.md).

Caveats:
- Pin to the **Snakemake 7 CLI**. Snakemake 8 changed resource and executor
  flags; if the container upgrades, only the codegen layer should change.
- Generated Snakefiles are an internal artifact. Users never edit them;
  error messages are translated back to step and module names.

### Scatter / gather (v1)

- Pipeline inputs may be a **sample collection** (list of libraries / SRRs /
  files keyed by `sample_id`, matching the existing `paired_end_libs[].sample_id`
  shape used by RNASeq and TaxonomicClassification).
- A step whose input port is single-valued and fed from a collection runs
  **once per sample** (scatter, which becomes a `{sample}` wildcard).
- An input port with `cardinality: many` fed from a per-sample step
  **gathers** all samples (which becomes `expand(...)`).
- Data-dependent fan-out (e.g. per-bin after binning) uses Snakemake
  `checkpoint`s. Defer it unless a v1 pipeline needs it.

### Tool environments

A module may set `environment: <name>` to run in a separately sourced
environment (conda env or source script under a configured root) when the
tool is not yet in the container. The default is `container`. `modpipe lint`
reports non-container modules, so they can be tracked until they land in
the image. These modules are allowed for now; eventually the only valid
environment will be `container`.

Resource policy (decided 2026-11-03): one pipeline is one Slurm job, capped like the big services (about
32 CPU / 256 GB / 48 h). Any step needing a `kraken_db`-partition database (registry `requirements`)
routes the whole job there. Preflight aggregation: `cpu = max(step.cpu)` (or the width of the
widest parallel level), `memory = max(step.memory)`,
`runtime = sum(critical path)`, with a safety factor.

## 5. Pipeline definition

> **Implemented**: see [MODULE_SCHEMA.md](MODULE_SCHEMA.md#pipeline-definition-json-schema-modpipepipelinev1); validated by
> `bin/modpipe validate` (types, attributes, scatter/gather, params, databases, template constraints, version pins, resources).

The pipeline is submitted as the `pipeline` parameter of the
`ModularPipeline` app (JSON, so it fits the existing app-param path).
Example: [`pipelines/wgs_assembly_qc.json`](../pipelines/wgs_assembly_qc.json).

```json
{
  "schema": "modpipe/pipeline/v1",
  "name": "WGS assembly with QC",
  "inputs": {
    "reads": {"type": "reads.short.paired",
              "source": {"paired_end_libs": [{"read1": "/user@bvbrc/home/r1.fq.gz",
                                              "read2": "/user@bvbrc/home/r2.fq.gz"}]}}
  },
  "steps": {
    "trim":     {"module": "fastp",  "in": {"reads": "$inputs.reads"}},
    "assemble": {"module": "spades", "in": {"reads": "trim.trimmed_reads"},
                 "params": {"mode": "isolate"}},
    "qc":       {"module": "quast",  "in": {"contigs": "assemble.contigs"}}
  },
  "outputs": {
    "contigs": "assemble.contigs",
    "assembly_report": "qc.report"
  }
}
```

- Edges are written as `step.port` references, which makes the format easy to
  generate from a graphical builder.
- Unspecified params take module defaults. Curated templates are pipeline
  JSONs with some params locked or hidden (`"expose": [...]`).
- Inputs use the existing BV-BRC input shapes (`paired_end_libs`,
  `single_end_libs`, `srr_ids`, wsid paths, genome ids), so `ReadSet` staging
  works unchanged.

## 6. Validation (before submission and again in preflight)

1. Every `module` exists and the descriptor version is supported.
2. Every required input port is connected; no cycles.
3. Every edge type-checks (is-a + attribute constraints). On failure, report
   the closest converter path if one exists.
4. Params validate against module param specs (type, enum, range).
5. Pipeline outputs reference existing ports.
6. Resource estimate is within the scheduler's limits.

Exposed as `modpipe validate pipeline.json` and as `POST /api/validate`. The graph editor calls it after every
edit. Issues carry a location (`{severity, where, msg}`, e.g. `steps.qc.in.contigs`), so the UI can badge the
step or port, and the response includes per-step resolved output types and scatter. Before validating, single
available converters are inserted automatically (`auto_convert`), and editor state in the pipeline's `ui` key is
applied (`apply_ui`: disabled optional steps are removed with bypass rewiring). Empty data choices are errors.

## 7. Discovery API (for the UI builder)

> Implemented: `bin/modpipe list-modules --json`, `show <module>`, `compatible --from <module>.<output>`, and for the UI
> `GET /api/catalog` (types, converters, modules with ports and params, version hash),
> `/api/templates[/<name>]` and `/api/source_options`. The connection rule (`TypeSystem.connection`: yes / maybe /
> convert / no) is mirrored in the browser (`TypeLogic.js`) for instant checks while drawing.
> `tests/unit/test_compat_parity.py` keeps the two in sync.

- `modpipe list-modules [--category]`: module catalog with ports and params
  (JSON, same shape as app specs so existing UI form generators can be reused).
- `modpipe compatible --from spades.contigs`: list of `(module, port)` that
  can consume this output, used for "what can I connect next?" in the UI.
- `modpipe export-app-spec`: generates the `ModularPipeline.json` app spec.

## 8. Output handling

- Each step runs in `work/<step_id>/` and outputs are found by descriptor
  `path` patterns (or by an adapter's `collect_outputs`).
- Declared pipeline `outputs` are uploaded to
  `<output_path>/.<output_file>/` with wstypes from `types/wstypes.yaml`.
  Intermediate outputs are uploaded only if `keep_intermediates: true`.
- A `pipeline_run.json` (resolved DAG, module/tool versions, params, timings,
  container image) is always saved for provenance and re-runs.

### Indexing (decided 2026-11-03; deferred with RASTtk)
> Deferred 2026-11-03: no module produces GTOs until RASTtk modules exist.

Any RASTtk-annotated `annotation.gto` among a pipeline's outputs is **always** loaded into BV-BRC as a private
genome, as the Genome Annotation service does. The engine appends this load step automatically; it reuses
Genome Annotation's indexing path (to be located: `skip_indexing` / `indexing_url` handling).

### Versioning (decided 2026-11-03)
`pipeline_run.json` and saved pipelines record each module's descriptor `version` and the tool version
(from `reference/tools/index.json`). Re-runs warn when a tool version changed; a descriptor with a
different major version blocks the run until the pipeline is updated.

## 9. Repository layout (as first proposed; see README "Layout" for the current tree)

```
ModularService/
  app_specs/ModularPipeline.json
  service-scripts/App-ModularPipeline.pl
  lib/modpipe/            (Python package: registry, types, pipeline, executors, adapters, cli)
  modules/*.yaml          (module descriptors)
  types/types.yaml, types/wstypes.yaml
  pipelines/*.json        (curated templates)
  tests/                  (descriptor lint, type-check unit tests, tiny-data e2e in container)
  Makefile                (dev_container-compatible deploy)
```
