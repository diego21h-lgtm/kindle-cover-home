# Shared USB-only state for 0.2; stage-1 scripts remain unchanged.
set -eu
umask 077
LC_ALL=C; export LC_ALL
USB=${KCH_USB_ROOT:-/mnt/us}
case "$USB" in /*) ;; *) exit 2;; esac
[ -d "$USB" ] && [ ! -L "$USB" ] || exit 1
STATE="$USB/coverhome"
for dir in "$STATE" "$STATE/logs"; do
    [ ! -L "$dir" ] || { echo 'Unsafe symlink' >&2; exit 1; }
    mkdir -p "$dir"
done
[ ! -L "$STATE/logs/session.log" ] && [ ! -L "$STATE/logs/previous.log" ] || exit 1
# Keep one previous log, bounded across normal launches.
if [ -f "$STATE/logs/session.log" ]; then
    mv -f "$STATE/logs/session.log" "$STATE/logs/previous.log"
fi
exec >> "$STATE/logs/session.log" 2>&1
printf '\nKindle Cover Home 0.2.1 UTC: '; date -u
