#!/bin/bash
# Submit P4 discovery runs to Slurm as one job array per set, plus an optional summary job.
#
#   tests/discovery/submit.sh [options] <set>...        sets: names or paths, e.g. readqc 02_assembly, or "all"
#
# Options:
#   --only id1,id2     submit only these run ids (requires exactly one set)
#   --throttle N       max concurrent array tasks per set (default 6)
#   --partition P      default: compute
#   --account A        default: cli
#   --keep             keep work directories on the node (debugging)
#   --no-summary       don't submit the summary job
#   --dry-run          print the sbatch commands only
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
SIF=${MODPIPE_SIF:-$(cat "$REPO/singularity_container_ref.txt")}
PARTITION=compute; ACCOUNT=cli; THROTTLE=6; ONLY=""; DRY=0; SUMMARY=1; KEEP=""
SETS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --only) ONLY=$2; shift 2;;
        --throttle) THROTTLE=$2; shift 2;;
        --partition) PARTITION=$2; shift 2;;
        --account) ACCOUNT=$2; shift 2;;
        --keep) KEEP=1; shift;;
        --no-summary) SUMMARY=0; shift;;
        --dry-run) DRY=1; shift;;
        -h|--help) sed -n '2,15p' "$0"; exit 0;;
        all) for f in "$HERE"/sets/*.yaml; do SETS+=("$f"); done; shift;;
        *) f=$1
           [[ -f $f ]] || f=$(ls "$HERE"/sets/*"$1"*.yaml 2>/dev/null | head -1)
           [[ -n $f && -f $f ]] || { echo "no such set: $1" >&2; exit 1; }
           SETS+=("$(cd "$(dirname "$f")" && pwd)/$(basename "$f")"); shift;;
    esac
done
[[ ${#SETS[@]} -gt 0 ]] || { echo "usage: $0 [options] <set>...|all" >&2; exit 1; }
[[ -z $ONLY || ${#SETS[@]} -eq 1 ]] || { echo "--only needs exactly one set" >&2; exit 1; }
[[ -s $SIF ]] || { echo "container not found: $SIF" >&2; exit 1; }
[[ -s $REPO/tests/fixtures/data/fixtures_index.json ]] || { echo "fetch fixtures first: tests/fixtures/fetch_fixtures.py" >&2; exit 1; }

# helper runs inside the container (PyYAML lives there)
rd() { singularity exec "$SIF" python3 "$HERE/run_discovery.py" "$@" 2>/dev/null; }

JOBS=()
for SET in "${SETS[@]}"; do
    name=$(basename "$SET" .yaml)
    n=$(rd count "$SET")
    read -r cpus mem tlimit < <(rd resources "$SET")
    if [[ -n $ONLY ]]; then array=$(rd indices "$SET" "$ONLY"); else array="0-$((n-1))"; fi
    logdir="$HERE/logs/$name"; mkdir -p "$logdir"
    cmd=(sbatch --parsable --job-name "modpipe-disc-$name" --account "$ACCOUNT" --partition "$PARTITION"
         --cpus-per-task "$cpus" --mem "$mem" --time "$tlimit" --array "${array}%${THROTTLE}"
         --output "$logdir/%A_%a.out"
         --export "ALL,MODPIPE_REPO=$REPO,MODPIPE_SIF=$SIF,MODPIPE_SET=$SET${KEEP:+,MODPIPE_KEEP=1}"
         "$HERE/discovery.sbatch")
    echo "[$name] $n runs; array=$array; cpus=$cpus mem=$mem time=$tlimit"
    if [[ $DRY -eq 1 ]]; then echo "  ${cmd[*]}"; else jid=$("${cmd[@]}"); JOBS+=("$jid"); echo "  submitted job $jid"; fi
done

if [[ $SUMMARY -eq 1 && $DRY -eq 0 && ${#JOBS[@]} -gt 0 ]]; then
    dep=$(IFS=:; echo "afterany:${JOBS[*]}")
    scmd=(sbatch --parsable --job-name modpipe-disc-summary --account "$ACCOUNT" --partition "$PARTITION"
          --cpus-per-task 1 --mem 2G --time 00:15:00 --dependency "$dep" --output "$HERE/logs/summary-%j.out"
          --wrap "singularity exec $SIF python3 $HERE/run_discovery.py summarize")
    sid=$("${scmd[@]}")
    echo "summary job $sid (after ${JOBS[*]}) -> reference/tools/DISCOVERY.md"
fi
