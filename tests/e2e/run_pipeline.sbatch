#!/bin/bash
# End-to-end test: run one pipeline with `modpipe run` inside the container on a compute node.
# Prototype of what App-ModularPipeline will do in production (minus workspace staging/upload).
#   sbatch [--cpus-per-task N --mem M --time T] tests/e2e/run_pipeline.sbatch <pipeline.json> [snakemake|local]
#SBATCH --account=cli
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=tests/e2e/logs/%x-%j.out
set -uo pipefail
REPO=${MODPIPE_REPO:-$SLURM_SUBMIT_DIR}
SIF=${MODPIPE_SIF:-$(cat "$REPO/singularity_container_ref.txt")}
PIPE=$(readlink -f "$1"); EXEC=${2:-snakemake}
NAME=$(basename "$PIPE" .json)

BINDS=()
DATA_IMAGE=/vol/patric3/production/data-images/patric-data-2022-0119
[[ -d $DATA_IMAGE ]] && BINDS+=(-B "$DATA_IMAGE:/opt/patric-common/data")
for d in /vol/bvbrc/production/application-backend /vol/blastdb/bvbrc-service /vol/patric3/metagenome_dbs; do
    [[ -d $d ]] && BINDS+=(-B "$d")
done
for s in /disks/tmp /scratch/tmp /tmp; do [[ -d $s && -w $s ]] && { SCRATCH=$s; break; }; done
RUN=$SCRATCH/$USER/modpipe-e2e/$NAME-$SLURM_JOB_ID
mkdir -p "$RUN"; BINDS+=(-B "$SCRATCH")
echo "node=$(hostname) pipeline=$NAME executor=$EXEC cpus=$SLURM_CPUS_PER_TASK mem=${SLURM_MEM_PER_NODE}M run=$RUN"

singularity exec "${BINDS[@]}" "$SIF" "$REPO/bin/modpipe" run "$PIPE" --workdir "$RUN" --executor "$EXEC" \
    --cores "$SLURM_CPUS_PER_TASK" --mem "$((SLURM_MEM_PER_NODE / 1024))G"
rc=$?

# Copy back the small stuff: provenance, outputs (dereferenced), Snakefile, per-job logs.
DEST=$REPO/tests/e2e/results/$NAME
rm -rf "$DEST"; mkdir -p "$DEST"
cp "$RUN/pipeline_run.json" "$DEST/" 2>/dev/null
[[ -d $RUN/outputs ]] && cp -rL "$RUN/outputs" "$DEST/"
[[ -f $RUN/.modpipe/Snakefile ]] && cp "$RUN/.modpipe/Snakefile" "$DEST/"
(cd "$RUN" && find steps -path '*/.modpipe/*' \( -name 'job.log' -o -name 'cmd.sh' -o -name 'time.txt' -o -name 'stderr.txt' \) \
    -size -2M -exec cp --parents {} "$DEST/" \;)
du -sh "$DEST"
rm -rf "$RUN"
exit $rc
