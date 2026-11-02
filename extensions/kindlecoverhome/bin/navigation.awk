# Pure navigation reducer: awk -v count=N -v selected=N -v action=... -f ...
# No input devices, IPC or rendering here. Selection is zero based.
BEGIN {
    n = count + 0; s = selected + 0
    if (n < 1) { print 0; exit }
    if (s < 0 || s >= n) s = 0
    page = int(s / 6); cell = s % 6
    if (action == "left" && cell % 2 == 1) s--
    if (action == "right" && cell % 2 == 0 && s+1 < n) s++
    if (action == "up" && cell >= 2) s -= 2
    if (action == "down" && cell < 4 && s+2 < n) s += 2
    if (action == "next" && (page+1)*6 < n) s = (page+1)*6
    if (action == "previous" && page > 0) s = (page-1)*6
    print s
}
