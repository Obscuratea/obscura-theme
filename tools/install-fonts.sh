#!/usr/bin/env bash
# Download the open-licence fonts Obscura uses into ~/.local/share/fonts/obscura.
# Archivo, Inter, Geist Mono, Instrument Serif: all SIL Open Font License, from the google/fonts repository.
set -euo pipefail
dest=~/.local/share/fonts/obscura
base=https://github.com/google/fonts/raw/main/ofl
mkdir -p "$dest"

get() { # get <url path> <file name>
    local out="$dest/$2"
    [ -s "$out" ] && return 0
    echo "  downloading $2"
    curl -fsSL "$base/$1" -o "$out.part"
    # a TrueType file starts with 00 01 00 00 or 'true'; anything else (an HTML error page) is rejected
    case "$(head -c4 "$out.part" | od -An -tx1 | tr -d ' \n')" in
        00010000|74727565) mv "$out.part" "$out" ;;
        *) rm -f "$out.part"; echo "  $2 was not a font file, aborting" >&2; exit 1 ;;
    esac
}

get 'archivo/Archivo%5Bwdth%2Cwght%5D.ttf'               'Archivo[wdth,wght].ttf'
get 'archivo/Archivo-Italic%5Bwdth%2Cwght%5D.ttf'        'Archivo-Italic[wdth,wght].ttf'
get 'geistmono/GeistMono%5Bwght%5D.ttf'                  'GeistMono[wght].ttf'
get 'instrumentserif/InstrumentSerif-Regular.ttf'        'InstrumentSerif-Regular.ttf'
get 'instrumentserif/InstrumentSerif-Italic.ttf'         'InstrumentSerif-Italic.ttf'
# Inter is often installed system-wide; fetch it only if fontconfig can't find it
# (capture first: `fc-list | grep -q` under pipefail reports "not found" when grep exits early)
families=$(fc-list : family)
if ! grep -qiE '(^|,)Inter(,|$)' <<<"$families"; then
    get 'inter/Inter%5Bopsz%2Cwght%5D.ttf'               'Inter[opsz,wght].ttf'
    get 'inter/Inter-Italic%5Bopsz%2Cwght%5D.ttf'        'Inter-Italic[opsz,wght].ttf'
fi
fc-cache -f "$dest" >/dev/null
echo "fonts ready in $dest"
