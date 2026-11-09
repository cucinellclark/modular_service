# BV-BRC Modular Service

A new BV-BRC service concept: a catalog of **tool modules** (fastp, SPAdes, QUAST,
MAFFT, RAxML, Kraken2, …) with typed inputs/outputs, plus a way to **connect
compatible modules into custom pipelines** and run them inside the standard
BV-BRC container. New tools are added by dropping in a module descriptor;
nothing else in the service changes.

## Decisions so far (2026-11-02)

| Topic | Decision |
|---|---|
| Module granularity | **Underlying tools** (individual binaries), not whole App-* services |
| Execution model | **Generated Snakemake** + local dev runner ([ARCHITECTURE §4](docs/ARCHITECTURE.md#4-execution-backends)) |
| Per-tool execution (2026-11-05) | **GoWe**: one CWL tool per module (`modpipe export-cwl`) running the **ModularStep** app; on a GoWe worker until the app is registered ([GOWE.md](docs/GOWE.md), [SERVICE.md](docs/SERVICE.md)) |
| Service nodes | **Not allowed**: tool modules only |
| Scatter/gather | **In v1** |
| Tools not in container | Separate source environment allowed for now; container-only eventually |
| Language | **Perl shell, Python core**: thin `App-ModularPipeline.pl` (AppScript) + Python engine |
| Pipeline authors | **Both**: curated templates from devs plus a user-facing builder |
| Test UI (2026-11-03) | Dojo page in BV-BRC-Web (branch `modular-pipeline-ui`): template form + **graph editor** + JSON, via the modpipe API ([UI.md](docs/UI.md)) |

More decisions (types, databases, resources, versioning, UI): [OPEN_QUESTIONS.md](docs/OPEN_QUESTIONS.md).

## Status (2026-11-06)
- The engine, 51 modules and 17 curated templates are lint-clean, and every template passes end-to-end runs in the
  container on Slurm.
- The BV-BRC service shell (`App-ModularPipeline.pl`) is tested end to end and deployable with `make deploy-service`.
- The UI runs on dev-5 against `bin/modpipe serve` on ash. It has the form, the graph editor (instant plus server
  checks, auto converters, workspace save/open in `home/pipeline`) and a job list. A graph-built pipeline has run
  for real.
- Per-tool execution via GoWe: the **ModularStep** app runs one module per job (chains tested on Slurm), and
  `modpipe export-cwl` makes one CWL tool per module (tested with GoWe's `cwl-runner`). Release `21610b109b` has all
  51 tools registered and blessed on the ash GoWe server (`deploy/gowe/release.sh`). Not yet run through a worker
  ([GOWE.md](docs/GOWE.md)).
- Not live yet: the app needs registration and a container build (BV-BRC maintainers). The API doesn't verify
  tokens yet (see OPEN_QUESTIONS).

## Layout

```
README.md                      this file
docs/
  ENVIRONMENT.md               container, dev_container, how App-* services run, I/O conventions
  TOOL_INVENTORY.md            tools in the container, grouped, and which services use them
  SERVICE_CATALOG.md           existing 49 App-* services, inputs, and the tools they wrap
  ARCHITECTURE.md              proposed design: modules, type system, pipelines, execution
  MODULE_SCHEMA.md             module descriptor + pipeline JSON schema (v1), template context
  SERVICE.md                   the BV-BRC service: params, input staging, preflight, upload, testing
  GOWE.md                      running modules through GoWe: export-cwl, worker shim, server setup, releases
  DEPLOYMENT.md                make deploy-service layout, data-root lookup, going live
  SECURITY.md                  shell-injection hardening: quoting rule, patterns, identifier validation
  UI.md                        test UI: BV-BRC-Web ModularPipeline form + graph editor + modpipe API (bin/modpipe serve)
  GRAPH_EDITOR_PLAN.md         design of the graphical pipeline editor
  ADDING_A_MODULE.md           how to add a new tool module
  OPEN_QUESTIONS.md            decisions still needed
  PREPROCESSING.md             one-time/recurring harvesting of tool metadata
  TEST_DATA.md                 test fixture sources (nf-core, BV-BRC QA, genome IDs) and tiers
types/
  types.yaml                   data type vocabulary: types, formats (EDAM refs), attributes, converters
  wstypes.yaml                 type <-> BV-BRC workspace type mapping (+ observed production quirks)
resources/
  databases.yaml               installed reference-database registry (paths, binds, versions, status)
modules/                       51 module descriptors (v1): read QC, assembly, mapping, variants, taxonomy, annotation, typing, expression, homology, phylogeny
pipelines/                     17 curated templates (modpipe list-templates); test inputs in tests/templates/
app_specs/ModularPipeline.json BV-BRC app spec
service-scripts/App-ModularPipeline.pl  BV-BRC Perl shell (AppScript): preflight, staging, run, upload
lib/modpipe/                   engine (Python): types, registries, templates, pipeline validation, CLI, api.py (UI API)
bin/modpipe                    CLI entry point (lint | validate | plan | run | instantiate | serve | list-modules | list-templates | show | compatible)
reference/
  app_specs/                   snapshot of /opt/p3/deployment/services/app_service/app_specs (from container)
  app_specs_summary.txt        one-line-per-service parameter summary
  qa_test_inputs.tsv           inputs referenced by BV-BRC QA test jobs
  workspace_typeslist.txt      registered workspace types (2021 dev copy)
  workspace_types_known.json   all known workspace types with evidence (registered / observed / MCP enum)
  workspace_type_usage.json    workspace types production actually saved (2026 QA outputs)
  nfcore_edam_terms.json       EDAM terms + file patterns extracted from nf-core meta.yml
  types_coverage.md            how well types.yaml formats cover P4 discovery outputs
  container_runtime_bin.txt    listing of /opt/patric-common/runtime/bin in the container
  tools/                       per-tool harvested metadata (P1–P3), see tools/SUMMARY.md
tests/unit/                    unit tests: python3 -m unittest discover -s tests/unit
tests/pipelines/               runnable test pipelines on the fixtures
tests/e2e/                     run_pipeline.sbatch: full pipeline runs on compute nodes (see tests/e2e/README.md)
tests/app/                     run_app.sbatch + params: the BV-BRC service end to end (see docs/SERVICE.md)
tests/fixtures/
  manifest.json                test fixtures (nf-core pinned + BV-BRC genomes), tiers, sets, sha256
  fetch_fixtures.py            fetch/verify fixtures into tests/fixtures/data (gitignored)
tests/discovery/
  sets/*.yaml                  P4 run definitions (107 runs in 7 sets)
  run_discovery.py, submit.sh  run tools on fixtures via Slurm arrays; record outputs/runtime/RSS
tools/
  summarize_app_specs.py       regenerates app_specs_summary.txt
  tool_list.json               candidate tools + per-tool harvest overrides + nf-core mapping
  harvest_tool_info.py         P1: versions/help (run in container)
  mine_invocations.py          P2: BV-BRC command-line mining (run in container)
  import_nfcore.py             P3: copy nf-core meta.yml/main.nf
  build_tool_summary.py        combine P1–P3 into reference/tools/SUMMARY.md
  extract_qa_inputs.py         list SRA/workspace inputs used by QA tests
  check_types.py               validate types/wstypes/databases/modules; write types_coverage.md
Makefile                       dev_container module: make | test | lint | deploy-service
scripts/modpipe.py             deployed CLI entry (-> $KB_TOP/bin/modpipe)
singularity_container_ref.txt  path to the production container image
```

## Key paths

- Container: `/vol/patric3/production/containers/ubuntu-176-build12-2.sif`
- App specs (**inside the container**, not on the host):
  `/opt/p3/deployment/services/app_service/app_specs/`
- Dev container / module sources: `/home/ac.cucinell/bvbrc-dev/dev_container/modules/`

```bash
S=/vol/patric3/production/containers/ubuntu-176-build12-2.sif
singularity exec $S ls /opt/p3/deployment/services/app_service/app_specs/
```

## Quick start

```bash
bin/modpipe list-modules
bin/modpipe list-templates                         # curated pipelines for the template picker
bin/modpipe lint                                   # validate all module descriptors
bin/modpipe validate pipelines/wgs_assembly_qc.json
bin/modpipe plan pipelines/multi_sample_assembly.json   # resolved types, scatter/gather, job resources
bin/modpipe compatible --from spades.contigs       # what can consume this output?
python3 -m unittest discover -s tests/unit -p 'test_*.py'   # incl. API and browser-parity tests (needs node)

# prototype UI API (docs/UI.md); on ash for dev-5:
bin/modpipe serve --host 0.0.0.0 --port 12005

# execute (inside the container; tools come from the image)
sbatch tests/e2e/run_pipeline.sbatch tests/pipelines/wgs_portiera.json
```
Validation runs on the host (Python 3.11, PyYAML, Jinja2) and in the container (Python 3.10).

## Modules and templates

| Category | Modules |
|---|---|
| read QC / host removal | fastp, trim_galore, fastqc, filtlong, hostile; reports: multiqc |
| assembly / polishing | spades, megahit, flye, unicycler, racon, pilon; QC: quast |
| mapping | bwa_mem, minimap2, hisat2, kma (gene databases: CARD, VFDB); ivar_trim (primers); samtools_coverage |
| variants / consensus | bcftools_call, freebayes, snippy, ivar_variants, ivar_consensus, bcftools_consensus |
| taxonomy | kraken2, bracken |
| SARS-CoV-2 / typing | freyja_variants, freyja_demix, pangolin, mlst |
| annotation | prodigal, trnascan, minced, amrfinder, vigor4, genomad, checkv |
| expression | stringtie, htseq_count |
| homology / clustering | blast, diamond, mmseqs_search, mmseqs_cluster, cdhit |
| alignment / phylogeny | mafft, fasttree, iqtree2, raxml_ng |
| converters | seqtk_seq_fasta (reads -> FASTA), samtools_sort_index (SAM/BAM -> sorted, indexed BAM) |

Templates (`bin/modpipe list-templates`): wgs_assembly_qc, multi_sample_assembly, clean_assembly,
long_read_assembly, polished_long_read_assembly, hybrid_assembly, isolate_assembly_characterization, variant_calling,
taxonomic_profile, sars2_wastewater, sars2_consensus, rnaseq_expression, viral_genome_annotation, mobile_elements, protein_search,
align_and_tree, protein_phylogeny.
