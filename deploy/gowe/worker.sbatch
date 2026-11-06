#!/bin/bash
# One GoWe worker for modpipe tools, as a Slurm job on a compute node:
#   GOWE_SERVER=http://ash.cels.anl.gov:12007 sbatch deploy/gowe/worker.sbatch
# Group `modpipe` (the tools' gowe:Execution.worker_group), Apptainer runtime, production image, this checkout and
# the BV-BRC data folders bind-mounted. The worker key (if the server uses --worker-keys) is read from
# GOWE_WORKER_KEY_FILE (mode 600, outside every bind). The user's token is injected per task by the server.
#SBATCH --account=cli
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --job-name=gowe-modpipe
#SBATCH --output=deploy/gowe/logs/%x-%j.out
set -uo pipefail
REPO=${MODPIPE_REPO:-$SLURM_SUBMIT_DIR}
GOWE_DIR=${GOWE_DIR:-$HOME/bvbrc-dev/Copilot/Agents/GoWe}
SERVER=${GOWE_SERVER:?set GOWE_SERVER, e.g. http://ash.cels.anl.gov:12007}
for s in /disks/tmp /scratch/tmp /tmp; do [[ -d $s && -w $s ]] && { SCRATCH=$s; break; }; done
WD=$SCRATCH/$USER/gowe-worker-$SLURM_JOB_ID
mkdir -p "$WD/bin" && chmod 700 "$WD"
# Compute nodes ship `singularity` only; the worker calls `apptainer` (same CLI).
if ! command -v apptainer >/dev/null && command -v singularity >/dev/null; then
    ln -sf "$(command -v singularity)" "$WD/bin/apptainer"; export PATH=$WD/bin:$PATH
fi
ARGS=(--server "$SERVER" --name "modpipe-$SLURM_JOB_ID-$(hostname -s)" --group modpipe --runtime apptainer
      --workdir "$WD/tasks" --poll 5s --extra-bind "$REPO" --extra-bind "$SCRATCH"
      # advertise the Slurm allocation, not the whole node (auto-detect would see every CPU/GB on the host)
      --max-cpus "${SLURM_CPUS_PER_TASK:-4}" --max-mem "${SLURM_MEM_PER_NODE:-16384}")
for d in /vol/bvbrc/production/application-backend /vol/blastdb/bvbrc-service /vol/patric3/metagenome_dbs; do
    [[ -d $d ]] && ARGS+=(--extra-bind "$d")
done
[[ -n ${GOWE_WORKER_KEY_FILE:-} ]] && ARGS+=(--worker-key-file "$GOWE_WORKER_KEY_FILE")
echo "node=$(hostname) server=$SERVER work=$WD"
"$GOWE_DIR/bin/gowe-worker" "${ARGS[@]}"
rc=$?
echo "exit=$rc"
rm -rf "$WD"
exit $rc
