#!/bin/bash
# Run App-ModularPipeline (or App-ModularStep, when the params have a "module" key) as a real BV-BRC job would (minus the scheduler): inside the container, with production
# binds, KB_INTERACTIVE=1 (uses ~/.patric_token), writing results to the workspace output_path in the params file.
#   sbatch [--cpus-per-task N --mem M] tests/app/run_app.sbatch tests/app/<name>.params.json
#SBATCH --account=cli
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=tests/app/logs/%x-%j.out
set -uo pipefail
REPO=${MODPIPE_REPO:-$SLURM_SUBMIT_DIR}
SIF=${MODPIPE_SIF:-$(cat "$REPO/singularity_container_ref.txt")}
PARAMS=$(readlink -f "$1")
APP=${MODPIPE_APP:-$(python3 -c 'import json,sys; print("ModularStep" if "module" in json.load(open(sys.argv[1])) else "ModularPipeline")' "$PARAMS")}
BINDS=()
DATA_IMAGE=/vol/patric3/production/data-images/patric-data-2022-0119
[[ -d $DATA_IMAGE ]] && BINDS+=(-B "$DATA_IMAGE:/opt/patric-common/data")
for d in /vol/bvbrc/production/application-backend /vol/blastdb/bvbrc-service /vol/patric3/metagenome_dbs; do
    [[ -d $d ]] && BINDS+=(-B "$d")
done
for s in /disks/tmp /scratch/tmp /tmp; do [[ -d $s && -w $s ]] && { SCRATCH=$s; break; }; done
WD=$SCRATCH/$USER/modpipe-app/$(basename "$(dirname "$PARAMS")")-$(basename "$PARAMS" .json)-$SLURM_JOB_ID
mkdir -p "$WD"; BINDS+=(-B "$SCRATCH")
echo "node=$(hostname) app=$APP params=$PARAMS work=$WD"
cd "$WD"
# Auth: a token file from the UI API (MODPIPE_TOKEN_FILE) is passed via SINGULARITYENV_* (never on a command line);
# otherwise KB_INTERACTIVE=1 makes AppScript use ~/.patric_token.
ENVS="P3_ALLOCATED_CPU=$SLURM_CPUS_PER_TASK,P3_ALLOCATED_MEMORY=${SLURM_MEM_PER_NODE}M,MODPIPE_HOME=$REPO"
if [[ -n ${MODPIPE_TOKEN_FILE:-} && -r $MODPIPE_TOKEN_FILE ]]; then
    export SINGULARITYENV_P3_AUTH_TOKEN=$(cat "$MODPIPE_TOKEN_FILE")
    export SINGULARITYENV_KB_AUTH_TOKEN=$SINGULARITYENV_P3_AUTH_TOKEN
else
    ENVS="KB_INTERACTIVE=1,$ENVS"
fi
singularity exec --env "$ENVS" \
    "${BINDS[@]}" "$SIF" bash -c "export PERL5LIB=/opt/p3/deployment/lib:\$PERL5LIB; \
    perl $REPO/service-scripts/App-$APP.pl xx $REPO/app_specs/$APP.json $PARAMS" < /dev/null
rc=$?
echo "exit=$rc"
if [[ -n ${MODPIPE_TOKEN_FILE:-} ]]; then
    cp work/pipeline_run.json "$(dirname "$PARAMS")/pipeline_run.json" 2>/dev/null
    rm -f "$MODPIPE_TOKEN_FILE"
else
    cp work/pipeline_run.json "$REPO/tests/app/logs/$(basename "$PARAMS" .params.json)-$SLURM_JOB_ID.pipeline_run.json" 2>/dev/null
fi
rm -rf "$WD"
exit $rc
