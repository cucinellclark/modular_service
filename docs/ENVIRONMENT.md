# Environment & How BV-BRC Services Run

## 1. Container

`/vol/patric3/production/containers/ubuntu-176-build12-2.sif` (~39 GB). Everything
runs inside it. `PATH` inside:

```
/opt/p3/deployment/bin          # App-* service entrypoints, p3-* CLI, p3x-* utilities (~500)
/opt/patric-common/runtime/bin  # third-party bioinformatics tools (~980)
/usr/bin, /usr/lib/tigr-glimmer # distro-packaged tools (bwa, bowtie2, samtools, minimap2, ...)
```

Important directories inside the container:

| Path | Contents |
|---|---|
| `/opt/p3/deployment/services/app_service/app_specs/` | JSON app spec + Markdown doc per service |
| `/opt/p3/deployment/plbin/App-*.pl` | Perl service scripts (wrapped by `bin/App-*`) |
| `/opt/p3/deployment/pybin/` | Python service code |
| `/opt/p3/deployment/lib/` | Perl libs (`Bio::KBase::AppService::*`, `Bio::P3::*`) |
| `/opt/p3/deployment/workflows/bvbrc_*/` | Snakemake workflows used by newer services |
| `/opt/patric-common/runtime/` | tool installs (spades-4.0.0, flye-2.9.1, kraken2, R-4.2.3, conda, …) |
| `/opt/patric-common/data/` | reference data (DBs) |

`python3`, `perl`, `Rscript`, `snakemake`, and `java` all resolve under
`/opt/patric-common/runtime/bin` or `/usr/bin`.

## 2. Dev container

`/home/ac.cucinell/bvbrc-dev/dev_container` is a KBase-style dev container
(`bootstrap`, `user-env.sh`, `make deploy`). Checked-out modules in `modules/`:

`app_service, bvbrc_gene_tree, bvbrc_ha_subtype_conversion, bvbrc_metacats,
codon_trees, comparative_systems_service, homology_service, p3_auth, p3_cli,
p3_code, p3_core, p3_deployment, p3diffexp, p3_msa, seed_core, seed_gjo,
seed_rast, sra_import, typecomp, Workspace`

A service module typically has:

```
<module>/
  app_specs/<AppId>.json        # parameter spec (copied into app_service at deploy)
  service-scripts/App-<AppId>.pl
  lib/ scripts/ Makefile
```

## 3. Anatomy of an App-* service

Framework: `Bio::KBase::AppService::AppScript`
(`modules/app_service/lib/Bio/KBase/AppService/AppScript.pm`).

```perl
my $script = Bio::KBase::AppService::AppScript->new(\&run, \&preflight);
exit $script->run(\@ARGV);
```

- **Invocation**: `App-X <service-url> <app_spec.json> <params.json>`
  (`--preflight out.json` runs preflight only).
- **preflight(app, app_def, raw_params, params)** returns
  `{cpu, memory, runtime, storage, policy_data, ...}` used by the scheduler
  (Slurm). The modular service will need to **aggregate** step requirements here.
- **run(app, app_def, raw_params, params)** does the work. `$app->workspace`,
  `$app->token`, `$app->result_folder` are available. `P3_ALLOCATED_CPU` is set.
- **Outputs**: written to the workspace under `<output_path>/.<output_file>/`
  (hidden result folder) plus a job-result object at `<output_path>/<output_file>`.
  Files are saved with a workspace type (`contigs`, `genome`, `html`, `svg`,
  `json`, `nwk`, …) via `$ws->save_file_to_file(...)` or `p3-cp ... ws:<folder>`
  with a suffix→type map.

### App spec format

```json
{ "id": "MSA", "script": "App-MSA", "label": "...", "description": "...",
  "parameters": [
    { "id": "aligner", "type": "enum", "enum": ["Muscle","Mafft"], "default": "Muscle",
      "required": 0, "allow_multiple": false, "label": "...", "desc": "..." },
    { "id": "fasta_files", "type": "group", "allow_multiple": true,
      "group": [ { "id": "file", "type": "wstype", "wstype": "feature_protein_fasta" }, ... ] },
    { "id": "output_path", "type": "folder", "required": 1 },
    { "id": "output_file", "type": "wsid",   "required": 1 } ] }
```

Parameter types seen: `string, int, float, bool/boolean, enum, list, array,
group, wstype, wsid, folder`. **App specs describe only inputs; outputs are
undeclared** and live in per-service conventions. That gap is the main
thing the modular service has to fill.

Input workspace types seen: `ReadFile, Contigs, Genome/genome, genbank_file,
feature_protein_fasta, feature_dna_fasta, aligned_dna_fasta,
aligned_protein_fasta, feature_group, genome_group, genome_fasta, tsv,
ExpList, ExpMetadata, model, media, template_model, probanno`.

## 4. Existing patterns for chaining

1. **Parent/child jobs**: `ComprehensiveGenomeAnalysis`
   (`lib/Bio/P3/GenomeAnnotationApp/ComprehensiveGenomeAnalysis.pm`) calls
   `Bio::KBase::AppService::Client->start_app("GenomeAssembly2", $params, $folder)`,
   polls `await_task_completion`, then finds outputs by convention
   (`<folder>/.assembly/assembly_contigs.fasta`,
   `details/assembly_run_details.json`) and feeds them to `GenomeAnnotation`.
   It also has an **inline** mode that runs `App-GenomeAssembly2 xx spec params.json`
   inside the same job.
2. **Perl shell + Snakemake**: `App-TaxonomicClassification.pl`,
   `App-SARS2Wastewater.pl`, `CoreGenomeMLST`, `WholeGenomeSNPAnalysis`.
   Perl uses `Bio::KBase::AppService::ReadSet` to stage reads (incl. SRR
   download), writes `config.json`, runs
   `python3 /opt/p3/deployment/workflows/<wf>/snakefile/wrapper.py config.json`,
   then uploads with `p3-cp --recursive` + suffix map. **This is the closest
   template for our "Perl shell, Python core" service.**
3. **Python drivers**: `p3x-assembly.py` (assembly recipes),
   `fastq_utils.py`, `run_rnaseq.py`, `reference_guided_assembly.py`: Python
   wrappers already containing tool command lines we can mine.

## 5. Useful commands

```bash
S=/vol/patric3/production/containers/ubuntu-176-build12-2.sif
singularity exec $S bash -c 'command -v spades.py; spades.py --version'
singularity exec $S cat /opt/p3/deployment/plbin/App-TaxonomicClassification.pl
python3 tools/summarize_app_specs.py reference/app_specs
```
