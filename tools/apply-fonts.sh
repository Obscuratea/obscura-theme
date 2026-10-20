#!/usr/bin/env bash
# Apply the Obscura fonts. Plasma Global Themes can't carry fonts, so this sets them directly.
# Sizes follow whatever size you already use for the UI font. Run again with SIZE=10 etc. to change.
set -euo pipefail
size=${SIZE:-$(kreadconfig6 --file kdeglobals --group General --key font | cut -d, -f2)}
size=${size:-11}
f() { echo "$1,$2,-1,5,${3:-400},0,0,0,0,0,0,0,0,0,0,1"; }
w() { kwriteconfig6 --file kdeglobals --group "$1" --key "$2" "$3"; }
w General font "$(f Inter "$size")"
w General menuFont "$(f Inter "$size")"
w General toolBarFont "$(f Inter "$size")"
w General smallestReadableFont "$(f Inter $((size - 2)))"
w General fixed "$(f 'Geist Mono' "$size")"
w WM activeFont "$(f Archivo "$size" 600)"
dbus-send --session --type=signal /KGlobalSettings org.kde.KGlobalSettings.notifyChange int32:1 int32:0
echo "fonts set: Inter / Geist Mono / Archivo at ${size}pt"
