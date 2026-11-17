#!/bin/bash
# Instantiate every curated template with its test inputs and submit each as an e2e Slurm job.
#   tests/templates/run_all.sh [template ...]
set -euo pipefail
REPO=$(cd "$(dirname "$0")/../.." && pwd); cd "$REPO"
GEN=tests/e2e/generated; mkdir -p "$GEN" tests/e2e/logs
names=("$@"); [[ ${#names[@]} -gt 0 ]] || names=($(ls tests/templates/*.json | xargs -n1 basename | sed 's/\.json$//'))
# "_variant_<template>_<tag>" files instantiate <template> with alternative params
for n in "${names[@]}"; do
    rc=0; python3 - "$n" <<'PY' || rc=$?
import json, sys
sys.path.insert(0, "lib")
from modpipe.templates import instantiate
n = sys.argv[1]
t = json.load(open(f"tests/templates/{n}.json"))
tmpl = t.get("template") or n
p = instantiate(tmpl, t.get("inputs"), t.get("params"))
p["name"] = "TEMPLATE TEST " + p["name"]
from modpipe.registry import DatabaseRegistry, ModuleRegistry
from modpipe.types import TypeSystem
mods = ModuleRegistry(TypeSystem(), DatabaseRegistry())
svc = [s["module"] for s in p["steps"].values() if mods.get(s["module"]) and mods.get(s["module"]).service]
if svc:   # service modules (whole BV-BRC apps) only run through GoWe, not `modpipe run`
    print(f"skip: uses service module(s) {', '.join(svc)} (GoWe only)")
    sys.exit(3)
json.dump(p, open(f"tests/e2e/generated/tmpl_{n}.json", "w"), indent=1)
PY
    if [[ $rc == 3 ]]; then echo "$n -> skipped (GoWe only)"; continue; fi
    [[ $rc == 0 ]] || exit $rc
    for i in 1 2 3; do
        j=$(sbatch --parsable --job-name "e2e-tmpl_$n" tests/e2e/run_pipeline.sbatch "$GEN/tmpl_$n.json" snakemake 2>/dev/null) && break
        sleep 20
    done
    echo "$n -> job ${j:-SUBMIT FAILED}"
done
