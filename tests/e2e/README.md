# End-to-end pipeline tests

Run complete pipelines from `tests/pipelines/` with `modpipe run` inside the BV-BRC container on a compute
node. This is a prototype of the production job (App-ModularPipeline), without the workspace staging and
upload, which the Perl shell will do.

```bash
python3 tests/fixtures/fetch_fixtures.py --container $(cat singularity_container_ref.txt)    # once
sbatch tests/e2e/run_pipeline.sbatch tests/pipelines/wgs_portiera.json            # Snakemake executor
sbatch tests/e2e/run_pipeline.sbatch tests/pipelines/wgs_portiera.json local      # local executor
```
Defaults: account `cli`, partition `compute`, 16 CPUs, 64 GB, 2 h (override with sbatch options).
The run happens in node scratch. `tests/e2e/results/<pipeline>/` gets `pipeline_run.json`, `outputs/` (dereferenced)
with `manifest.json`, the Snakefile and per-job logs, then the scratch run is deleted. Results and logs are gitignored.

| Pipeline | What it exercises | Wall time (16 CPU) |
|---|---|---|
| `align_tree_sarscov2.json` | MAFFT L-INS-i -> FastTree LG (protein `type_from`) | ~15 s |
| `wgs_portiera.json` | fastp -> SPAdes -> QUAST with a BV-BRC reference fetched by genome id (`p3-genome-fasta`) | ~1 min |
| `multi_sample_bfragilis.json` | scatter (fastp, SPAdes per sample) + gather (one QUAST for all) | ~1 min |

Interactive alternative for small pipelines (login node, in the container):
```bash
singularity exec -B /tmp $(cat singularity_container_ref.txt) bin/modpipe run tests/pipelines/align_tree_sarscov2.json \
    --workdir /tmp/$USER/tree --executor local --cores 4 --mem 8G
```
