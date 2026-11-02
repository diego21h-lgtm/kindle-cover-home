#!/bin/sh
set -eu
# Private worker invoked by find. Books are identified by extension, never executed/opened.
file=$1
name=${file##*/}
ext=${name##*.}
ext=$(printf '%s' "$ext" | tr 'A-Z' 'a-z')
case "$ext" in mobi|azw|azw3|prc|pdf|txt) ;; *) exit 0;; esac
[ ! -L "$file" ] || exit 0
title=${name%.*}
cover=
# Only exact-basename sidecars; no claim that they are embedded/valid covers.
base=${file%.*}
for candidate in "$base.jpg" "$base.jpeg" "$base.png"; do
    if [ -f "$candidate" ] && [ ! -L "$candidate" ]; then cover=$candidate; break; fi
done
# TSV escapes: backslash -> \\, TAB -> \t, CR -> \r, LF -> \n.
# awk operates on lines; explicit record separator preserves embedded newlines.
escape() {
    printf '%s\n' "$1" | awk 'BEGIN {first=1} {if (!first) printf "\\n"; first=0; for(i=1;i<=length($0);i++){c=substr($0,i,1); if(c=="\\") printf "\\\\"; else if(c=="\t") printf "\\t"; else if(c=="\r") printf "\\r"; else printf "%s",c}}'
}
if ! (
    escape "$title"; printf '\t'; escape 'Desconhecido'; printf '\t%s\t' "$ext"
    escape "$file"; printf '\t'; escape "$cover"; printf '\tfilename\n'
) >> "$KCH_SCAN_OUTPUT"; then
    : > "$KCH_SCAN_ERROR"
    exit 1
fi
