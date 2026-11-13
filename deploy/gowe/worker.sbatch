#!/bin/bash
# One GoWe worker for modpipe tools, as a Slurm job on a compute node:
#   GOWE_SERVER=http://ash.cels.anl.gov:12007 sbatch deploy/gowe/worker.sbatch     (from the repo root, or set MODPIPE_REPO)
# Group `modpipe` (the tools' gowe:Execution.worker_group), Apptainer runtime, production image, the released code
# snapshots (deploy/gowe/release.sh: ~/GoWeServer/modpipe/releases, read-only) and the BV-BRC data folders
# bind-mounted. MODPIPE_RELEASES overrides the releases folder (a dev checkout works too, for unreleased tools). The worker key (if the server uses --worker-keys) is read from
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
RELEASES=${MODPIPE_RELEASES:-$HOME/GoWeServer/modpipe/releases}
GOWE_DIR=${GOWE_DIR:-$HOME/bvbrc-dev/Copilot/Agents/GoWe}
SERVER=${GOWE_SERVER:?set GOWE_SERVER, e.g. http://ash.cels.anl.gov:12007}
for s in /disks/tmp /scratch/tmp /tmp; do [[ -d $s && -w $s ]] && { SCRATCH=$s; break; }; done
WD=$SCRATCH/$USER/gowe-worker-$SLURM_JOB_ID
mkdir -p "$WD/bin" && chmod 700 "$WD"
# Some compute nodes have only singularity-ce; the worker calls `apptainer`. The wrapper also maps the
# APPTAINERENV_* tool environment (the injected token) to SINGULARITYENV_*, which a bare symlink would drop.
if ! command -v apptainer >/dev/null && command -v singularity >/dev/null; then
    cp "${MODPIPE_REPO:-$SLURM_SUBMIT_DIR}/deploy/gowe/apptainer-on-singularity.sh" "$WD/bin/apptainer" || exit 1
    chmod 755 "$WD/bin/apptainer"; export PATH=$WD/bin:$PATH
    echo "apptainer: singularity wrapper ($(singularity --version))"
fi
ARGS=(--server "$SERVER" --name "modpipe-$SLURM_JOB_ID-$(hostname -s)" --group modpipe --runtime apptainer
      --workdir "$WD/tasks" --poll 5s --extra-bind "$RELEASES" --extra-bind "$SCRATCH"
      # advertise the Slurm allocation, not the whole node (auto-detect would see every CPU/GB on the host)
      --max-cpus "${SLURM_CPUS_PER_TASK:-4}" --max-mem "${SLURM_MEM_PER_NODE:-16384}")
for d in /vol/bvbrc/production/application-backend /vol/blastdb/bvbrc-service /vol/patric3/metagenome_dbs; do
    [[ -d $d ]] && ARGS+=(--extra-bind "$d")
done
[[ -n ${GOWE_WORKER_KEY_FILE:-} ]] && ARGS+=(--worker-key-file "$GOWE_WORKER_KEY_FILE")
# Persistent image sha256 cache (seeded by release.sh): skips the ~10 min hash of the 37 GB image before the first
# token task. Must stay outside every bind (it is under ~/GoWeServer/modpipe, of which only releases/ is bound).
DIGESTS=${MODPIPE_IMAGE_DIGESTS:-$HOME/GoWeServer/modpipe/image-digests.json}
[[ -d $(dirname "$DIGESTS") ]] && ARGS+=(--image-digest-file "$DIGESTS")
echo "node=$(hostname) server=$SERVER releases=$RELEASES work=$WD"
"$GOWE_DIR/bin/gowe-worker" "${ARGS[@]}"
rc=$?
echo "exit=$rc"
rm -rf "$WD"
exit $rc
