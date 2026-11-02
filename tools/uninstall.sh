#!/bin/sh
set -eu
[ "$#" -eq 1 ] || { echo 'Usage: sh tools/uninstall.sh /absolute/USB/root' >&2; exit 2; }
USB=$1
case "$USB" in /*) ;; *) exit 2;; esac
DEST="$USB/extensions/kindlecoverhome"
[ -d "$USB/documents" ] && [ ! -L "$USB" ] && [ ! -L "$USB/extensions" ] && [ ! -L "$DEST" ] || exit 1
[ -d "$DEST" ] || { echo 'Already absent'; exit 0; }
[ -f "$DEST/.kch-owned" ] && [ ! -L "$DEST/.kch-owned" ] || { echo 'Ownership marker missing; refusing removal.' >&2; exit 1; }
[ ! -L "$DEST/bin" ] && [ ! -L "$DEST/ui" ] && [ ! -L "$DEST/ui/demo" ] || exit 1
# Delete only shipped files. Additional user files prevent rmdir and remain intact.
for file in config.xml menu.json demo.tsv .kch-owned bin/common.sh bin/start.sh bin/diagnose.sh bin/catalog-entry.sh bin/session.sh bin/launch.sh bin/navigation.awk bin/render.sh bin/library.sh ui/demo/count ui/demo/catalog.tsv ui/demo/page-1-select-0.png ui/demo/page-1-select-1.png ui/demo/page-1-select-2.png ui/demo/page-1-select-3.png ui/demo/page-1-select-4.png ui/demo/page-1-select-5.png; do
    rm -f "$DEST/$file"
done
for dir in "$DEST/ui/demo" "$DEST/ui"; do
    [ ! -L "$dir" ] || exit 1
    [ ! -d "$dir" ] || rmdir "$dir"
done
rmdir "$DEST/bin" "$DEST"
echo 'Extension removed. Data preserved in kindle-cover-home-data and coverhome.'
