#!/bin/bash
# Run a generated CWL tool/workflow (modpipe export-cwl) with GoWe's standalone cwl-runner + Apptainer on a compute
# node, the way a GoWe worker would: production image, repo + BV-BRC data bind-mounted, the user's token injected
# as KB_AUTH_TOKEN/BVBRC_TOKEN through a mode-600 env file (never on a command line).
#   sbatch tests/cwl/run_cwl.sbatch <tool-or-workflow.cwl> <job.json>
# GOWE_DIR: GoWe checkout with bin/cwl-runner (default ~/bvbrc-dev/Copilot/Agents/GoWe).
#SBATCH --account=cli
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=tests/cwl/logs/%x-%j.out
set -uo pipefail
REPO=${MODPIPE_REPO:-$SLURM_SUBMIT_DIR}
RUNNER=${GOWE_DIR:-$HOME/bvbrc-dev/Copilot/Agents/GoWe}/bin/cwl-runner
CWL=$(readlink -f "$1"); JOB=$(readlink -f "$2")
for s in /disks/tmp /scratch/tmp /tmp; do [[ -d $s && -w $s ]] && { SCRATCH=$s; break; }; done
WD=$SCRATCH/$USER/modpipe-cwl/$(basename "$JOB" .json)-$SLURM_JOB_ID
mkdir -p "$WD" && chmod 700 "$WD"
BINDS=(--extra-bind "$REPO" --extra-bind "$SCRATCH")
for d in /vol/bvbrc/production/application-backend /vol/blastdb/bvbrc-service /vol/patric3/metagenome_dbs; do
    [[ -d $d ]] && BINDS+=(--extra-bind "$d")
done
ENVF=$WD/token.env
( umask 077; t=$(cat "${MODPIPE_TOKEN_FILE:-$HOME/.patric_token}"); printf 'KB_AUTH_TOKEN=%s\nBVBRC_TOKEN=%s\n' "$t" "$t" > "$ENVF" )
# Compute nodes ship `singularity` only; cwl-runner calls `apptainer` (same CLI).
if ! command -v apptainer >/dev/null && command -v singularity >/dev/null; then
    # wrapper, not a symlink: it maps APPTAINERENV_* (the injected token) to SINGULARITYENV_*
    mkdir -p "$WD/bin" && cp "$REPO/deploy/gowe/apptainer-on-singularity.sh" "$WD/bin/apptainer" \
        && chmod 755 "$WD/bin/apptainer" && export PATH=$WD/bin:$PATH
fi
echo "node=$(hostname) cwl=$CWL job=$JOB work=$WD"
cd "$WD"
TMPDIR=$WD "$RUNNER" --runtime apptainer "${BINDS[@]}" --env-file "$ENVF" --outdir "$WD/out" -j 2 "$CWL" "$JOB"
rc=$?
rm -f "$ENVF"
echo "exit=$rc"
[[ $rc == 0 ]] && rm -rf "$WD"
exit $rc
