#!/bin/sh
# Desktop POSIX shell (Linux/macOS/WSL); Windows Explorer installation is documented.
set -eu
[ "$#" -eq 1 ] || { echo 'Usage: sh tools/install.sh /absolute/USB/root' >&2; exit 2; }
USB=$1
case "$USB" in /*) ;; *) exit 2;; esac
[ -d "$USB/documents" ] && [ ! -L "$USB" ] && [ ! -L "$USB/extensions" ] || exit 1
HERE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DEST="$USB/extensions/kindlecoverhome"
[ ! -e "$DEST" ] && [ ! -L "$DEST" ] || { echo 'Destination exists; preserve it and uninstall first.' >&2; exit 1; }
mkdir -p "$USB/extensions"
# Reserve destination atomically. A failed copy remains explicit, never overwrites another install.
mkdir "$DEST"
cp -R "$HERE/extensions/kindlecoverhome/." "$DEST/"
printf 'Installed: %s\n' "$DEST"
