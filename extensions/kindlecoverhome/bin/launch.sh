#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MODE=${1:-scan}
case "$MODE" in scan|demo|diagnose) ;; *) exit 2;; esac
. "$HERE/session.sh"
printf 'mode=%s\n' "$MODE"
if [ "$MODE" = diagnose ]; then
    sh "$HERE/diagnose.sh"
else
    sh "$HERE/start.sh" "$MODE"
    cat "$USB/kindle-cover-home-data/diagnostics.txt"
fi
printf '\ncompleted mode=%s\n' "$MODE"
