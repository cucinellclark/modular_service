# The BV-BRC services: App-ModularPipeline and App-ModularStep

Two apps share one Perl shell (`lib/ModularPipeline/AppCommon.pm`, on `Bio::KBase::AppService::AppScript`) and the
Python core (`bin/modpipe`):

| app | runs | used by |
|---|---|---|
| `ModularPipeline` (`app_specs/ModularPipeline.json`, `service-scripts/App-ModularPipeline.pl`) | a whole pipeline in one job (Snakemake inside) | the prototype UI today |
| `ModularStep` (`app_specs/ModularStep.json`, `service-scripts/App-ModularStep.pl`) | **one module** per job | GoWe workflows (one CWL tool per module), on a GoWe worker until the app is registered with the BV-BRC scheduler |

## Parameters
| id | meaning |
|---|---|
| `pipeline` | a full `modpipe/pipeline/v1` object ([MODULE_SCHEMA.md](MODULE_SCHEMA.md)) |
| `pipeline_template` | name of a curated pipeline in `pipelines/` (template-picker UI path) |
| `inputs` | with a template: `{input name: source}`, where the source is a data source as below; every template input is required |
| `template_params` | with a template: `{"<step>.params.<id>": value}`, only for the template's `expose` list |
| `keep_intermediates` | also save every step output under `steps/<step>/<port>/` |
| `output_path`, `output_file` | as for every service: results go to `<output_path>/.<output_file>/` |

Give either `pipeline` or `pipeline_template`, not both. `modpipe instantiate` performs the template fill, so the
UI can preview it.

## ModularStep parameters
Flat, so that a generated CWL tool maps 1:1 onto them (GoWe's BV-BRC executor passes CWL inputs to `start_app` as
top-level keys; AppScript keeps undeclared keys in `raw_params`):

| key | meaning |
|---|---|
| `module` | module id (required) |
| `<input port>` | data for that port (see below); required ports must be given |
| `<parameter id>` | module parameter value (module defaults otherwise) |
| `input_types` | optional `{port: concrete type}` when the type can't be inferred |
| `output_path`, `output_file` | as for every service |

Any other key is refused (keys starting with `_` are ignored). A port value is:
- a **workspace path**: a file (type from its `modpipe_type` metadata, else from its workspace type via
  `wstypes.yaml` `accept`, if that leaves one candidate the port accepts), or an **output folder** of an earlier
  ModularStep/ModularPipeline job (`.../.<job>/<output>[/<sample>]`), whose metadata carries type, attributes, parts
  and sample id;
- a **list** of those (a list port gathers them; a single port runs once per item);
- a **source object** as below, or `{"type": T, "source": {...}}`.

The type of an abstract port (e.g. `reads.short`) comes from, in order: `{"type"}`, `input_types`, workspace
metadata, the source shape (`paired_end_libs`/`srr_ids` -> `reads.short.paired`, `single_end_libs` ->
`reads.short.single`), or the port's only concrete subtype; otherwise the step is refused, naming `input_types.<port>`.
`modpipe step-pipeline params.json [--ws-meta meta.json]` builds and validates the one-step pipeline (the app runs
it, after looking up the workspace paths' metadata). Outputs that the module's `when:` rules switch off for these
parameters are left out.

Example chain (each line one job; `T=/user@bvbrc/home/tests`):
```json
{"module": "fastp", "reads": {"srr_ids": ["SRR2838702"]}, "output_path": "T", "output_file": "s1"}
{"module": "minimap2", "reads": "T/.s1/trimmed_reads/SRR2838702", "reference": {"genome_ids": ["511145.12"]},
 "input_types": {"reference": "sequences.dna.contigs"}, "output_path": "T", "output_file": "s2"}
{"module": "samtools_coverage", "alignment": "T/.s2/alignment/SRR2838702", "output_path": "T", "output_file": "s3"}
```

## Input sources (what the shell stages)
| source key | staged by | becomes |
|---|---|---|
| `paired_end_libs`, `single_end_libs`, `srr_ids`, `srr_libs` | `Bio::KBase::AppService::ReadSet` (validate, localize, stage_in; SRA download included) | local read files; SRA accession = sample id |
| `wsid`, `wsids`, `files` (workspace paths) | `AppScript::stage_in` | local files |
| `genome_group` | `P3DataAPI::retrieve_patric_ids_from_genome_group` | `genome_ids` (fetched by modpipe with `p3-genome-fasta`) |
| `genome_ids` | modpipe (`p3-genome-fasta --contig`) | local FASTA per genome |
| `feature_group` | `P3DataAPI` protein/nucleotide sequences, chosen by the input type | local FASTA |
| `fasta_data` | written to a file | local FASTA |
| `feature_ids` | `P3DataAPI::retrieve_protein/nucleotide_feature_sequence` | local FASTA |
| `database_file` | modpipe (registry `files`, e.g. `artic_v4.1:reference`) | local file |
| `parts` | `AppScript::stage_in`, one subdirectory per item | multi-file values: `{bam, index}`, `{vcf, index}`, `{representatives, membership}`, ... (a dict, or a list of dicts with optional `sample_id`) |

Read inputs are checked for pairing: a paired type with single-end libraries fails early, and vice versa.

## Flow
1. **preflight**: resolve the pipeline (template) and run `modpipe validate --json`. It returns
   `cpu`, `memory`, `runtime` (plan x 1.2 + 30 min), `storage` (5 x staged read size from ReadSet, else 20 GB) and
   `policy_data` (`partition`/`constraint`, e.g. `kraken_db`). Invalid pipelines fail here, before queueing.
2. **run**: validate, stage inputs (rewriting every source to local files), then
   `modpipe run --executor snakemake --cores $P3_ALLOCATED_CPU --mem $P3_ALLOCATED_MEMORY`.
3. **upload** (also on failure, for debugging): `pipeline.json` (as submitted), `pipeline_run.json`
   (provenance), and every `outputs/manifest.json` entry to `<result folder>/<output>[/<sample>]/<file>`, saved with
   its workspace type (`types/wstypes.yaml`). Files over 10 MB go through Shock. The job result object (written by
   AppScript) lists them.
   - Each `<output>[/<sample>]` folder is one **output value**, created with workspace metadata `modpipe_type`,
     `modpipe_attrs` (JSON), `modpipe_files` (JSON `{part or "_": file name}`) and `modpipe_sample`; each file
     carries `modpipe_type` (+ `modpipe_part`). That folder can be passed straight to a ModularStep input port.
   - `outputs.json` in the result folder: `{output: [{folder, type, attrs, files: {part or "_": ws path}, sample}]}`
     (ModularStep also returns it as the job output).
   ModularStep declares every output port of its module as an output, so all of them are saved.

Locating the Python core: `MODPIPE_HOME`, else `<script dir>/..` (dev checkout), else `$KB_TOP/bin/modpipe`. The
scripts add `<script dir>/../lib` to `@INC` for `ModularPipeline::AppCommon` (deployed: `$TARGET/lib`).

## Testing
`tests/app/run_app.sbatch tests/app/<name>.params.json` runs the service exactly as `p3x-run-qa.pl` does
(`singularity exec --env KB_INTERACTIVE=1 ... App-<app> xx spec params`) on a compute node, writing to the
workspace folder in the params file. The app is ModularStep when the params have a `module` key, else
ModularPipeline (`MODPIPE_APP` overrides). `KB_INTERACTIVE=1` uses `~/.patric_token`, so that token must belong to
the owner of the output folder. Preflight only:
```bash
singularity exec --env KB_INTERACTIVE=1 $(cat singularity_container_ref.txt) bash -c \
  'PERL5LIB=/opt/p3/deployment/lib perl service-scripts/App-ModularPipeline.pl --preflight pf.json xx app_specs/ModularPipeline.json tests/app/<name>.params.json'
```
| params file | exercises |
|---|---|
| `feature_group_tree.params.json` | feature group -> protein FASTA -> MAFFT -> FastTree |
| `genome_group_quast.params.json` | genome group (Brucella) -> collection of genomes -> QUAST (gather) |
| `genome_group_too_short.params.json` | **negative test**: a group of 71-99 bp fragments; QUAST must fail, the job result must have `success=0`, and `pipeline.json`/`pipeline_run.json` must still be saved |
| `template_wgs_srr.params.json` | curated template + exposed params; SRA download via ReadSet; reference by genome id |
| `ms1_mafft` -> `ms2_fasttree` | ModularStep: feature group + `input_types`; then an output folder (alignment) as input |
| `ms3_fastp` -> `ms4_minimap2` -> `ms5_coverage` | ModularStep: SRA reads; paired output folder with sample id; BAM+index folder (`parts`) |

Results of the first runs (2026-11-03, results in `/clark.cucinell@patricbrc.org/home/ModularService_tests`):
feature_group_tree OK (15 s), template_wgs_srr OK (SRA download + template, 64 s), genome_group_too_short failed as
expected (`success=0`). Both apps exit non-zero when the job fails (2026-11-05 fix: `AppScript::run` returns the raw
wait status, and `exit 65280` wrapped to 0). Submit chains with `sbatch --dependency=afterok:<job>`.

ModularStep chains (2026-11-05, same folder): `ms1_mafft` -> `ms2_fasttree` OK (24 s + 14 s; the tree read the
alignment folder by its metadata). `ms3_fastp` (SRA download, 69 s) -> `ms4_minimap2` -> `ms5_coverage` OK: the
paired-reads folder carried type and sample id, the BAM+index folder carried `sorted=coordinate`, and every output
landed under `<output>/SRR2838702/`. A first try showed SRA inputs losing their sample folder (fixed: SRA accessions
count as sample ids) and that a refused step now fails the Slurm job.
