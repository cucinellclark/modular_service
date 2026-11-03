#!/bin/bash
# Run App-ModularPipeline as a real BV-BRC job would (minus the scheduler): inside the container, with production
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
BINDS=()
DATA_IMAGE=/vol/patric3/production/data-images/patric-data-2022-0119
[[ -d $DATA_IMAGE ]] && BINDS+=(-B "$DATA_IMAGE:/opt/patric-common/data")
for d in /vol/bvbrc/production/application-backend /vol/blastdb/bvbrc-service /vol/patric3/metagenome_dbs; do
    [[ -d $d ]] && BINDS+=(-B "$d")
done
for s in /disks/tmp /scratch/tmp /tmp; do [[ -d $s && -w $s ]] && { SCRATCH=$s; break; }; done
WD=$SCRATCH/$USER/modpipe-app/$(basename "$PARAMS" .params.json)-$SLURM_JOB_ID
mkdir -p "$WD"; BINDS+=(-B "$SCRATCH")
echo "node=$(hostname) params=$PARAMS work=$WD"
cd "$WD"
singularity exec --env KB_INTERACTIVE=1,P3_ALLOCATED_CPU=$SLURM_CPUS_PER_TASK,P3_ALLOCATED_MEMORY=${SLURM_MEM_PER_NODE}M,MODPIPE_HOME=$REPO \
    "${BINDS[@]}" "$SIF" bash -c "export PERL5LIB=/opt/p3/deployment/lib:\$PERL5LIB; \
    perl $REPO/service-scripts/App-ModularPipeline.pl xx $REPO/app_specs/ModularPipeline.json $PARAMS" < /dev/null
rc=$?
echo "exit=$rc"
cp work/pipeline_run.json "$REPO/tests/app/logs/$(basename "$PARAMS" .params.json)-$SLURM_JOB_ID.pipeline_run.json" 2>/dev/null
rm -rf "$WD"
exit $rc
