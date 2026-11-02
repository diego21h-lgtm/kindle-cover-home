#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
case "${1:-scan}" in scan|demo) MODE=${1:-scan};; *) echo 'Usage: start.sh [scan|demo]' >&2; exit 2;; esac
. "$HERE/common.sh"
sh "$HERE/diagnose.sh" > "$LOCK/diagnostics.txt" 2>&1
mv -f "$LOCK/diagnostics.txt" "$DATA/diagnostics.txt"
if [ "$MODE" = demo ]; then
    cat "$HERE/../demo.tsv" > "$LOCK/demo.tsv"
    mv -f "$LOCK/demo.tsv" "$DATA/demo.tsv"
else
    DOCS="$USB/documents"
    [ -d "$DOCS" ] && [ ! -L "$DOCS" ] || { echo 'documents directory missing or symlink' >&2; exit 1; }
    printf 'title\tauthor\tformat\tpath\tcover_candidate\tmetadata_source\n' > "$LOCK/catalog.tsv"
    export KCH_SCAN_OUTPUT="$LOCK/catalog.tsv" KCH_SCAN_ERROR="$LOCK/scan-error"
    # find does not follow symlinks. Per-file argv preserves whitespace and metacharacters.
    find "$DOCS" -type f -exec sh "$HERE/catalog-entry.sh" '{}' \;
    [ ! -f "$KCH_SCAN_ERROR" ] || { echo 'Catalog generation failed' >&2; exit 1; }
    mv -f "$LOCK/catalog.tsv" "$DATA/catalog.tsv"
fi
printf 'Kindle Cover Home: %s completed. Results: %s\n' "$MODE" "$DATA"
