#!/bin/sh
# Standalone read-only collector; redirect stdout to a file on the USB storage.
set -eu
LC_ALL=C
export LC_ALL
printf 'Kindle Cover Home 0.1.0 - diagnostics\n'
printf 'Expected target: B023 / firmware 4.1.4 (not automatically certified)\n'
printf '\nUTC time\n'; date -u
printf '\nKernel / architecture\n'; uname -srm
for item in /etc/prettyversion.txt /proc/version /proc/meminfo /proc/bus/input/devices /proc/fb; do
    printf '\n--- %s ---\n' "$item"
    if [ -r "$item" ]; then cat "$item"; else printf 'unavailable\n'; fi
done
printf '\nTool presence only (no invocation)\n'
for tool in sh find awk sed tr date uname eips fbink lipc-get-prop lipc-set-prop dbus-send; do
    if command -v "$tool" >/dev/null 2>&1; then printf '%s: present\n' "$tool"; else printf '%s: absent\n' "$tool"; fi
done
printf '\nDevice node metadata only (no reads/grabs/writes)\n'
for item in /dev/fb0 /dev/input/event*; do
    [ -e "$item" ] || continue
    ls -l "$item"
done
for item in /sys/class/graphics/fb0/name /sys/class/graphics/fb0/virtual_size /sys/class/graphics/fb0/bits_per_pixel; do
    if [ -r "$item" ]; then printf '\n--- %s ---\n' "$item"; cat "$item"; fi
done
printf '\nNo framebuffer writes, input capture, framework stop, LIPC calls or book opening performed.\n'
