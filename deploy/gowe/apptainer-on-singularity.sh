#!/bin/bash
# `apptainer` for compute nodes that only have singularity-ce (3.10 on e.g. fir; lemon has Apptainer 1.5).
# A plain symlink is not enough: GoWe passes the tool environment (including the injected BV-BRC token) as
# APPTAINERENV_<NAME>, which singularity-ce ignores (it reads SINGULARITYENV_<NAME>), so the token would be
# silently dropped. Copy each APPTAINERENV_* to SINGULARITYENV_* (values are never printed), then exec singularity.
# Installed as $WD/bin/apptainer by deploy/gowe/worker.sbatch and tests/cwl/run_cwl.sbatch.
for v in $(compgen -e); do
    case $v in
        APPTAINERENV_*) export "SINGULARITYENV_${v#APPTAINERENV_}=${!v}" ;;
    esac
done
exec singularity "$@"
