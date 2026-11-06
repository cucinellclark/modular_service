#!/bin/bash
# Release the current ModularService commit to the GoWe server: a read-only snapshot of the code, the 51 modpipe
# CWL tools pointing into it, registered and blessed (token injection) for the `modpipe` worker group.
#
#   deploy/gowe/release.sh [--dry-run] [--yes] [--skip-tests]
#
#   --dry-run     check and print what would happen; change nothing
#   --yes         bless without a prompt per tool (gowe still prints each review report; all are saved in the release)
#   --skip-tests  don't run the unit tests (they must have passed for this commit some other way)
#
# Why a snapshot: a blessing pins the tool document and the image, but the code the tools run is bind-mounted from
# outside the image. Pointing the tools at an immutable per-commit copy puts the commit into every tool's content,
# so a blessing covers exactly that code, and development in the working checkout can't change what the server runs.
#
# Steps (stops at the first failure):
#   1 checks: clean checkout, HEAD pushed to origin, unit tests, GoWe healthy, gowe CLI logged in
#   2 snapshot: git archive HEAD -> $RELEASES/<sha>/, then chmod -R a-w (an existing snapshot is reused as-is)
#   3 image sha256 (cached per image path + size + mtime)
#   4 modpipe export-cwl --modpipe-home <snapshot> --out <snapshot>/cwl/tools (run from the snapshot)
#   5 register as modpipe-<module> (register_tools.py; token from MODPIPE_TOKEN_FILE, never argv)
#   6 gowe admin bless <wf id> --image-sha256 <sha> --groups modpipe --note "modpipe <sha>"
#   7 RELEASE.json (+ bless reports) in the snapshot; $BASE/current -> this release
# Not done: restarting GoWe, starting workers, revoking older blessings (each points at its own frozen snapshot).
#
# Environment: GOWE_SERVER (default http://localhost:12007), GOWE_DIR (GoWe checkout with bin/gowe),
# MODPIPE_RELEASE_BASE (default ~/GoWeServer/modpipe), MODPIPE_TOKEN_FILE (default ~/.patric_token).
set -euo pipefail

DRY=0; YES=0; TESTS=1
for a in "$@"; do
    case "$a" in
        --dry-run) DRY=1 ;;
        --yes) YES=1 ;;
        --skip-tests) TESTS=0 ;;
        -h|--help) sed -n '2,27p' "$0"; exit 0 ;;
        *) echo "unknown option $a" >&2; exit 2 ;;
    esac
done

REPO=$(cd "$(dirname "$0")/../.." && pwd)
SERVER=${GOWE_SERVER:-http://localhost:12007}
GOWE=${GOWE_DIR:-$HOME/bvbrc-dev/Copilot/Agents/GoWe}/bin/gowe
BASE=${MODPIPE_RELEASE_BASE:-$HOME/GoWeServer/modpipe}
RELEASES=$BASE/releases
IMAGE=$(cat "$REPO/singularity_container_ref.txt")
GROUP=modpipe

say() { printf '\n== %s\n' "$*"; }
die() { printf 'release: %s\n' "$*" >&2; exit 1; }
run() { if (( DRY )); then printf '   (dry run) %s\n' "$*"; else "$@"; fi; }

cd "$REPO"
SHA=$(git rev-parse HEAD); SHORT=${SHA:0:10}
DEST=$RELEASES/$SHORT

# ---------------------------------------------------------------- 1 checks
say "1 checks (commit $SHORT)"
[[ -z $(git status --porcelain) ]] || die "the checkout has uncommitted or untracked changes (git status); commit first"
git fetch -q origin || die "git fetch origin failed"
git merge-base --is-ancestor HEAD "origin/$(git rev-parse --abbrev-ref HEAD)" 2>/dev/null \
    || die "HEAD $SHORT is not on origin/$(git rev-parse --abbrev-ref HEAD); push it first"
if (( TESTS )); then
    python3 -m pytest -q tests/unit >/tmp/modpipe-release-tests.$$ 2>&1 || { tail -20 /tmp/modpipe-release-tests.$$; rm -f /tmp/modpipe-release-tests.$$; die "unit tests failed"; }
    tail -1 /tmp/modpipe-release-tests.$$; rm -f /tmp/modpipe-release-tests.$$
fi
curl -sf "$SERVER/api/v1/health" | grep -q '"healthy"' || die "GoWe at $SERVER is not healthy"
[[ -x $GOWE ]] || die "no gowe CLI at $GOWE (set GOWE_DIR)"
[[ -s $HOME/.gowe/credentials.json ]] || die "the gowe CLI is not logged in; run:  $GOWE login < ~/.patric_token"
[[ -r $IMAGE ]] || die "image $IMAGE not readable"
echo "   ok: clean, pushed, server healthy, image $IMAGE"

# ---------------------------------------------------------------- 2 snapshot
say "2 snapshot -> $DEST"
if [[ -d $DEST ]]; then
    echo "   exists; reusing it unchanged"
else
    run mkdir -p "$RELEASES"
    if (( ! DRY )); then
        tmp=$(mktemp -d "$RELEASES/.tmp-$SHORT-XXXX")
        git archive "$SHA" | tar -x -C "$tmp"
        printf '%s\n' "$SHA" > "$tmp/RELEASE_COMMIT"
        chmod -R a-w "$tmp"; chmod u+w "$tmp"                  # top dir stays writable until step 7
        mv "$tmp" "$DEST"
    else
        echo "   (dry run) git archive $SHA | tar -x -C $DEST; chmod -R a-w"
    fi
fi

# ---------------------------------------------------------------- 3 image sha256
say "3 image sha256"
mkdir -p "$BASE/image-sha256"
key=$(stat -c '%s-%Y' "$IMAGE")-$(printf '%s' "$IMAGE" | sha1sum | cut -c1-12)
cache=$BASE/image-sha256/$key
if [[ -s $cache ]]; then
    IMG_SHA=$(cat "$cache"); echo "   cached: $IMG_SHA"
elif (( DRY )); then
    IMG_SHA="<sha256 of $IMAGE>"; echo "   (dry run) sha256sum $IMAGE"
else
    echo "   hashing $IMAGE ($(du -h "$IMAGE" | cut -f1)) ..."
    IMG_SHA=$(sha256sum "$IMAGE" | cut -d' ' -f1); printf '%s\n' "$IMG_SHA" > "$cache"; echo "   $IMG_SHA"
fi

# ---------------------------------------------------------------- 4 export
say "4 export-cwl (tools run $DEST/bin/modpipe)"
TOOLS=$DEST/cwl/tools
if (( DRY )); then
    echo "   (dry run) $DEST/bin/modpipe export-cwl --modpipe-home $DEST --image $IMAGE --out $TOOLS"
elif [[ -d $TOOLS ]]; then
    echo "   exists; reusing"
else
    chmod u+w "$DEST" && mkdir -p "$DEST/cwl" && chmod u+w "$DEST/cwl"
    PYTHONDONTWRITEBYTECODE=1 "$DEST/bin/modpipe" export-cwl --modpipe-home "$DEST" --image "$IMAGE" --out "$TOOLS"
    chmod -R a-w "$DEST/cwl"
fi

# ---------------------------------------------------------------- 5 register
say "5 register on $SERVER"
REG=$DEST/registered.json
if (( DRY )); then
    echo "   (dry run) register_tools.py --server $SERVER --dir $TOOLS --json-out $REG"
else
    chmod u+w "$DEST"
    GOWE_SERVER=$SERVER python3 "$REPO/deploy/gowe/register_tools.py" --dir "$TOOLS" --json-out "$REG.tmp"
    mv "$REG.tmp" "$REG"
fi

# ---------------------------------------------------------------- 6 bless
say "6 bless for group $GROUP (image $IMG_SHA)"
if (( DRY )); then
    echo "   (dry run) for each tool: $GOWE --server $SERVER admin bless <wf id> --image-sha256 <sha> --groups $GROUP --note \"modpipe $SHORT\"$( (( YES )) && echo ' --yes')"
else
    mkdir -p "$DEST/bless"
    yes_flag=(); tty=/dev/tty
    if (( YES )); then yes_flag=(--yes); tty=/dev/null; fi
    # only this release's tools still awaiting a blessing: one already blessed (an earlier, interrupted run) is
    # skipped, since blessing the same hash again is a CONFLICT
    pending=$("$GOWE" --server "$SERVER" admin blessings --pending --json) || die "could not list pending blessings"
    python3 -c '
import json, sys
reg = json.load(open(sys.argv[1]))
pend = {p["workflow_id"] for p in json.loads(sys.argv[2]).get("pending") or []}
for m, d in sorted(reg.items()):
    if d["id"] in pend:
        print(m, d["id"])
    else:
        print("   modpipe-%s (%s): already blessed, skipping" % (m, d["id"]), file=sys.stderr)
' "$REG" "$pending" |
    while read -r mid wfid; do
        echo "-- modpipe-$mid ($wfid)"
        # report to the terminal and to bless/<module>.txt; the prompt (without --yes) reads the terminal
        "$GOWE" --server "$SERVER" admin bless "$wfid" --image-sha256 "$IMG_SHA" --groups "$GROUP" \
            --note "modpipe $SHORT ($SHA)" "${yes_flag[@]}" < "$tty" 2>&1 | tee "$DEST/bless/$mid.txt"
        [[ ${PIPESTATUS[0]} == 0 ]] || die "bless failed for modpipe-$mid (report: $DEST/bless/$mid.txt)"
    done
fi

# ---------------------------------------------------------------- 7 record
say "7 record"
if (( DRY )); then
    echo "   (dry run) write $DEST/RELEASE.json; $BASE/current -> releases/$SHORT"
else
    python3 - "$DEST" "$SHA" "$IMAGE" "$IMG_SHA" "$SERVER" "$GROUP" <<'PY'
import datetime, getpass, json, os, socket, sys
dest, sha, image, img_sha, server, group = sys.argv[1:]
reg = json.load(open(os.path.join(dest, "registered.json")))
json.dump({"commit": sha, "released": datetime.datetime.now().isoformat(timespec="seconds"),
           "by": getpass.getuser(), "host": socket.gethostname(), "server": server, "worker_group": group,
           "image": image, "image_sha256": img_sha, "tools": reg},
          open(os.path.join(dest, "RELEASE.json"), "w"), indent=1)
PY
    chmod -R a-w "$DEST"
    ln -sfn "releases/$SHORT" "$BASE/current"
    echo "   $DEST/RELEASE.json; $BASE/current -> releases/$SHORT"
fi
say "done: modpipe $SHORT"
