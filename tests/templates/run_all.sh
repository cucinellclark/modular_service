#!/bin/bash
# Instantiate every curated template with its test inputs and submit each as an e2e Slurm job.
#   tests/templates/run_all.sh [template ...]
set -euo pipefail
REPO=$(cd "$(dirname "$0")/../.." && pwd); cd "$REPO"
GEN=tests/e2e/generated; mkdir -p "$GEN" tests/e2e/logs
names=("$@"); [[ ${#names[@]} -gt 0 ]] || names=($(ls tests/templates/*.json | xargs -n1 basename | sed 's/\.json$//'))
for n in "${names[@]}"; do
    python3 - "$n" <<'PY'
import json, sys
sys.path.insert(0, "lib")
from modpipe.templates import instantiate
n = sys.argv[1]
t = json.load(open(f"tests/templates/{n}.json"))
p = instantiate(n, t.get("inputs"), t.get("params"))
p["name"] = "TEMPLATE TEST " + p["name"]
json.dump(p, open(f"tests/e2e/generated/tmpl_{n}.json", "w"), indent=1)
PY
    for i in 1 2 3; do
        j=$(sbatch --parsable --job-name "e2e-tmpl_$n" tests/e2e/run_pipeline.sbatch "$GEN/tmpl_$n.json" snakemake 2>/dev/null) && break
        sleep 20
    done
    echo "$n -> job ${j:-SUBMIT FAILED}"
done
