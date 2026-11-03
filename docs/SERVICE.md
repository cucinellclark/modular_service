# The BV-BRC service: App-ModularPipeline

`app_specs/ModularPipeline.json` + `service-scripts/App-ModularPipeline.pl` (Perl shell on
`Bio::KBase::AppService::AppScript`) + `bin/modpipe` (Python core).

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

## Input sources (what the shell stages)
| source key | staged by | becomes |
|---|---|---|
| `paired_end_libs`, `single_end_libs`, `srr_ids`, `srr_libs` | `Bio::KBase::AppService::ReadSet` (validate, localize, stage_in; SRA download included) | local read files; SRA accession = sample id |
| `wsid`, `wsids`, `files` (workspace paths) | `AppScript::stage_in` | local files |
| `genome_group` | `P3DataAPI::retrieve_patric_ids_from_genome_group` | `genome_ids` (fetched by modpipe with `p3-genome-fasta`) |
| `genome_ids` | modpipe (`p3-genome-fasta --contig`) | local FASTA per genome |
| `feature_group` | `P3DataAPI` protein/nucleotide sequences, chosen by the input type | local FASTA |
| `fasta_data` | written to a file | local FASTA |
| `feature_ids` | not yet supported | |

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

Locating the Python core: `MODPIPE_HOME`, else `<script dir>/..` (dev checkout), else
`$KB_TOP/modules/ModularService`. Deployment packaging is still to do.

## Testing
`tests/app/run_app.sbatch tests/app/<name>.params.json` runs the service exactly as `p3x-run-qa.pl` does
(`singularity exec --env KB_INTERACTIVE=1 ... App-ModularPipeline xx spec params`) on a compute node, writing to the
workspace folder in the params file. Preflight only:
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

Results of the first runs (2026-11-03, results in `/clark.cucinell@patricbrc.org/home/ModularService_tests`):
feature_group_tree OK (15 s), template_wgs_srr OK (SRA download + template, 64 s), genome_group_too_short failed as
expected (`success=0`). Outside the scheduler, AppScript exits 0 even when the job fails; the job result's `success` flag is
what counts.
