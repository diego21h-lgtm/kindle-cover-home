#!/bin/sh
# First application entry point: record progress BEFORE dirname/cd/session/log setup.
# The menu passes this file to /bin/sh with absolute paths and separate params.
USB=${KCH_USB_ROOT:-/mnt/us}
case "$USB" in /*) ;; *) exit 2;; esac
[ -d "$USB" ] && [ ! -L "$USB" ] || exit 1
TRACE="$USB/coverhome-bootstrap.log"
[ ! -L "$TRACE" ] || exit 1
# One fresh trace per action, independent from coverhome/logs.
exec > "$TRACE" 2>&1 || exit 1
printf '%s\n' 'Kindle Cover Home 0.2.1' 'BOOTSTRAP_ENTERED'
# EXIT logs failures from path checks, cd, mkdir, or the child shell.
trap 'result=$?; printf "BOOTSTRAP_EXIT=%s\n" "$result"' 0
trap 'exit 1' 1 2 15
set -eu
umask 077
printf 'SHELL_STARTED pid=%s\n' "$$"
printf 'INITIAL_CWD='; pwd
TARGET=${1:-probe}
MODE=${2:-diagnose}
case "$TARGET:$MODE" in
    probe:diagnose|launch:scan|launch:demo|launch:diagnose|library:demo|library:catalog|library:left|library:right|library:up|library:down|library:next|library:previous|library:select|library:back|library:show) ;;
    *) echo 'INVALID_ARGUMENTS'; exit 2;;
esac
ROOT="$USB/extensions/kindlecoverhome"
printf 'EXPECTED_ROOT=%s\n' "$ROOT"
[ -d "$ROOT" ] && [ ! -L "$ROOT" ] && [ ! -L "$ROOT/bin" ] || { echo 'ROOT_UNAVAILABLE'; exit 1; }
SCRIPT="$ROOT/bin/$TARGET.sh"
if [ "$TARGET" != probe ]; then
    [ -f "$SCRIPT" ] && [ -r "$SCRIPT" ] && [ ! -L "$SCRIPT" ] || { echo 'SCRIPT_UNREADABLE'; exit 1; }
    printf 'SCRIPT_LOCATED=%s\n' "$SCRIPT"
    # -n parses without running: distinguish syntax/CRLF errors from application errors.
    /bin/sh -n "$SCRIPT" || { echo 'SHELL_SYNTAX_FAILED'; exit 1; }
    echo 'SHELL_SYNTAX_OK'
fi
cd "$ROOT" || { echo 'CHDIR_FAILED'; exit 1; }
echo 'CWD_READY'
for dir in "$USB/coverhome" "$USB/coverhome/logs"; do
    [ ! -L "$dir" ] || { echo 'LOG_PATH_SYMLINK'; exit 1; }
    mkdir -p "$dir" || { echo 'LOG_DIRECTORY_FAILED'; exit 1; }
done
echo 'LOG_DIRECTORY_READY'
PROBE="$USB/coverhome/logs/bootstrap-probe.txt"
[ ! -L "$PROBE" ] || { echo 'LOG_PROBE_SYMLINK'; exit 1; }
printf '%s\n' 'Kindle Cover Home 0.2.1' 'LOG_WRITE_OK' > "$PROBE" || { echo 'LOG_WRITE_FAILED'; exit 1; }
echo 'LOG_WRITE_OK'
if [ "$TARGET" = probe ]; then echo 'PROBE_COMPLETED'; exit 0; fi
printf 'CHILD_START target=%s mode=%s\n' "$TARGET" "$MODE"
# Keep control after nonzero child exit; session.sh may redirect all child output.
set +e
/bin/sh "$SCRIPT" "$MODE"
result=$?
set -e
printf 'CHILD_EXIT=%s\n' "$result"
exit "$result"
