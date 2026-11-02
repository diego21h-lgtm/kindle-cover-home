#!/bin/sh
set -eu
[ "$#" -eq 1 ] || { echo 'Usage: sh tools/uninstall.sh /absolute/USB/root' >&2; exit 2; }
USB=$1
case "$USB" in /*) ;; *) exit 2;; esac
DEST="$USB/extensions/kindlecoverhome"
[ -d "$USB/documents" ] && [ ! -L "$USB" ] && [ ! -L "$USB/extensions" ] && [ ! -L "$DEST" ] || exit 1
[ -d "$DEST" ] || { echo 'Already absent'; exit 0; }
[ -f "$DEST/.kch-owned" ] && [ ! -L "$DEST/.kch-owned" ] || { echo 'Ownership marker missing; refusing removal.' >&2; exit 1; }
[ ! -L "$DEST/bin" ] || exit 1
# Delete only shipped files. Additional user files prevent rmdir and remain intact.
for file in config.xml menu.json demo.tsv .kch-owned bin/common.sh bin/start.sh bin/diagnose.sh bin/catalog-entry.sh; do
    rm -f "$DEST/$file"
done
rmdir "$DEST/bin" "$DEST"
echo 'Extension removed. Catalogs and diagnostics preserved in kindle-cover-home-data.'
