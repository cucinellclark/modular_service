# Template test inputs

One file per curated template in `pipelines/`: `{"inputs": {...}, "params": {...}}` filled with test fixtures,
used by `bin/modpipe instantiate <template> --inputs/--params` and by the unit tests (every template must have one
and must instantiate + validate). `run_all.sh` instantiates each one and submits it with `tests/e2e/run_pipeline.sbatch`.
