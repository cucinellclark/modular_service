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
| Service nodes | **Not allowed**: tool modules only |
| Scatter/gather | **In v1** |
| Tools not in container | Separate source environment allowed for now; container-only eventually |
| Language | **Perl shell, Python core**: thin `App-ModularPipeline.pl` (AppScript) + Python engine |
| Pipeline authors | **Both**: curated templates from devs plus a user-facing builder |

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
  DEPLOYMENT.md                make deploy-service layout, data-root lookup, going live
  ADDING_A_MODULE.md           how to add a new tool module
  OPEN_QUESTIONS.md            decisions still needed
  PREPROCESSING.md             one-time/recurring harvesting of tool metadata
  TEST_DATA.md                 test fixture sources (nf-core, BV-BRC QA, genome IDs) and tiers
types/
  types.yaml                   data type vocabulary: types, formats (EDAM refs), attributes, converters
  wstypes.yaml                 type <-> BV-BRC workspace type mapping (+ observed production quirks)
resources/
  databases.yaml               installed reference-database registry (paths, binds, versions, status)
modules/                       20 module descriptors (v1): read QC, assembly, mapping, variants, taxonomy, annotation, typing, phylogeny
pipelines/                     9 curated templates (modpipe list-templates); test inputs in tests/templates/
app_specs/ModularPipeline.json BV-BRC app spec
service-scripts/App-ModularPipeline.pl  BV-BRC Perl shell (AppScript): preflight, staging, run, upload
lib/modpipe/                   engine (Python): types, registries, templates, pipeline validation, CLI
bin/modpipe                    CLI entry point (lint | validate | plan | run | instantiate | list-modules | show | compatible)
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
python3 -m unittest discover -s tests/unit

# execute (inside the container; tools come from the image)
sbatch tests/e2e/run_pipeline.sbatch tests/pipelines/wgs_portiera.json
```
Validation runs on the host (Python 3.11, PyYAML, Jinja2) and in the container (Python 3.10).

## Modules and templates (2026-11-03)

| Category | Modules |
|---|---|
| read QC | fastp, filtlong |
| assembly | spades, flye, unicycler; assembly QC: quast |
| mapping / variants | bwa_mem, minimap2, bcftools_call, freebayes |
| taxonomy | kraken2, bracken |
| annotation / typing | prodigal, amrfinder, mlst |
| alignment / phylogeny | mafft, fasttree, iqtree2 |
| converters | seqtk_seq_fasta (reads -> FASTA), samtools_sort_index (SAM/BAM -> sorted, indexed BAM) |

Templates: wgs_assembly_qc, multi_sample_assembly, long_read_assembly, hybrid_assembly,
isolate_assembly_characterization, variant_calling, taxonomic_profile, align_and_tree, protein_phylogeny.
