#!/bin/sh
# An explicitly enabled, single-shot native image display. Never capture keys.
set -eu
[ "$#" -eq 1 ] || exit 2
IMAGE=$1
USB=${KCH_USB_ROOT:-/mnt/us}
# This file is a user's explicit acknowledgement AFTER checking eips on the device.
[ -f "$USB/coverhome/enable-eips" ] && [ ! -L "$USB/coverhome/enable-eips" ] || {
    echo 'BLOCKED: inspect device eips help/format; then create coverhome/enable-eips for a manual display experiment.' >&2
    exit 3
}
[ -f "$IMAGE" ] && [ ! -L "$IMAGE" ] || exit 1
# Fixed binary path: never execute a replacement supplied in catalog or environment.
[ -x /usr/sbin/eips ] || { echo 'BLOCKED: /usr/sbin/eips unavailable; no fallback framebuffer writes.' >&2; exit 3; }
echo 'Experimental eips -g PNG; Amazon may repaint. No framework changes.'
/usr/sbin/eips -g "$IMAGE"
