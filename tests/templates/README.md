# Template test inputs

One file per curated template in `pipelines/`: `{"inputs": {...}, "params": {...}}` filled with test fixtures,
used by `bin/modpipe instantiate <template> --inputs/--params` and by the unit tests (every template must have one
and must instantiate + validate). `run_all.sh` instantiates each one and submits it with `tests/e2e/run_pipeline.sbatch`.

Known test-data limits: `sars2_wastewater` runs on 100 SARS-CoV-2 read pairs, which is far too few for Freyja to
estimate lineages (coverage 0, uniform abundances). It checks the wiring, not the biology; use a real amplicon
sample for that. `rnaseq_expression` uses `feature_type: CDS` because the SARS-CoV-2 GTF has no exon features.
