# POSIX sh; sourced by entry points. No writes outside the USB data directory.
set -eu
umask 077
LC_ALL=C
export LC_ALL
# Override only for desktop fixtures; KUAL uses /mnt/us.
USB=${KCH_USB_ROOT:-/mnt/us}
case "$USB" in /*) ;; *) echo 'USB root must be absolute' >&2; exit 1;; esac
[ -d "$USB" ] && [ ! -L "$USB" ] || exit 1
DATA="$USB/kindle-cover-home-data"
[ ! -L "$DATA" ] || exit 1
mkdir -p "$DATA"
# A private directory created atomically prevents concurrent launches.
LOCK="$DATA/.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
    echo 'Already running, or stale lock: kindle-cover-home-data/.lock' >&2
    exit 1
fi
trap 'rm -f "$LOCK/catalog.tsv" "$LOCK/demo.tsv" "$LOCK/diagnostics.txt" "$LOCK/scan-error"; rmdir "$LOCK"' 0
trap 'exit 1' 1 2 15
