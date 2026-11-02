#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ACTION=${1:-demo}
case "$ACTION" in demo|catalog|left|right|up|down|next|previous|select|back|show) ;; *) exit 2;; esac
. "$HERE/session.sh"
printf 'library action=%s\n' "$ACTION"
LOCK="$STATE/.ui-lock"
mkdir "$LOCK" || { echo 'Another action active or stale lock'; exit 1; }
trap 'rm -f "$LOCK/state"; rmdir "$LOCK"' 0
trap 'exit 1' 1 2 15
FILE="$STATE/ui-state"
[ ! -L "$FILE" ] || exit 1
MODE=demo; SELECTED=0
if [ -f "$FILE" ]; then
    IFS=' ' read -r MODE SELECTED < "$FILE" || exit 1
fi
case "$MODE" in demo|catalog) ;; *) exit 1;; esac
case "$SELECTED" in ''|*[!0-9]*) exit 1;; esac
case "$ACTION" in demo|catalog) MODE=$ACTION; SELECTED=0;; esac
if [ "$ACTION" = back ]; then
    rm -f "$FILE"
    echo 'Session ended. No process or input handle remains. Use Back in KUAL to return.'
    exit 0
fi
if [ "$MODE" = demo ]; then ASSETS="$HERE/../ui/demo"; else ASSETS="$STATE/library"; fi
[ ! -L "$ASSETS" ] && [ -d "$ASSETS" ] || { echo 'Prepare library on the desktop; see docs/stage-2.md'; exit 1; }
[ ! -L "$ASSETS/count" ] || exit 1
COUNT=$(cat "$ASSETS/count")
case "$COUNT" in ''|*[!0-9]*) exit 1;; esac
# Bound state arithmetic and workload. Prepared libraries currently support up to 600 books.
[ "${#COUNT}" -le 3 ] && [ "$COUNT" -le 600 ] && [ "${#SELECTED}" -le 3 ] || exit 1
SELECTED=$(awk -v count="$COUNT" -v selected="$SELECTED" -v action="$ACTION" -f "$HERE/navigation.awk")
if [ "$ACTION" = select ]; then
    echo "Selection index=$SELECTED mode=$MODE; book opening intentionally unavailable."
    exit 0
fi
printf '%s %s\n' "$MODE" "$SELECTED" > "$LOCK/state"
mv -f "$LOCK/state" "$FILE"
PAGE=$((SELECTED / 6 + 1)); CELL=$((SELECTED % 6))
IMAGE="$ASSETS/page-$PAGE-select-$CELL.png"
printf 'count=%s page=%s selected=%s image=%s\n' "$COUNT" "$PAGE" "$SELECTED" "$IMAGE"
sh "$HERE/render.sh" "$IMAGE"
echo 'Display command returned successfully; visual result requires observation on the Kindle.'
