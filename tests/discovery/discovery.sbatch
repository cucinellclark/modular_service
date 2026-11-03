#!/bin/bash
# One array task = one discovery run. Submitted by submit.sh, which sets --cpus-per-task/--mem/--time/--array per set.
# Required env (exported by submit.sh): MODPIPE_REPO, MODPIPE_SIF, MODPIPE_SET
#SBATCH --nodes=1
#SBATCH --ntasks=1
set -uo pipefail

REPO=${MODPIPE_REPO:?}
SIF=${MODPIPE_SIF:?}
SET=${MODPIPE_SET:?}
IDX=${SLURM_ARRAY_TASK_ID:?}

# Same NFS data paths as the production slurm_batch.tt template (only those that exist on this node).
BINDS=()
DATA_IMAGE=/vol/patric3/production/data-images/patric-data-2022-0119
[[ -d $DATA_IMAGE ]] && BINDS+=(-B "$DATA_IMAGE:/opt/patric-common/data")
for d in /vol/bvbrc/production/application-backend /vol/blastdb/bvbrc-service /vol/patric3/metagenome_dbs; do
    [[ -d $d ]] && BINDS+=(-B "$d")
done

# Node-local scratch for the work directory (outputs are recorded, then deleted).
for s in ${MODPIPE_SCRATCH:-} /disks/tmp /scratch/tmp /tmp; do
    if [[ -n $s && -d $s && -w $s ]]; then SCRATCH=$s; break; fi
done
export MODPIPE_SCRATCH=$SCRATCH
BINDS+=(-B "$SCRATCH")

echo "node=$(hostname) set=$SET index=$IDX cpus=${SLURM_CPUS_PER_TASK:-?} mem=${SLURM_MEM_PER_NODE:-?}M scratch=$SCRATCH"
exec singularity exec "${BINDS[@]}" "$SIF" python3 "$REPO/tests/discovery/run_discovery.py" run "$SET" "$IDX" ${MODPIPE_KEEP:+--keep-workdir}
