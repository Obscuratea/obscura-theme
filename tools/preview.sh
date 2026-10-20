#!/usr/bin/env bash
# Render the preview gallery against a scratch config. Never touches ~/.config.
# Usage: preview.sh <dark|light> [#accent]
set -euo pipefail
here=$(cd "$(dirname "$0")/.." && pwd)
variant=${1:-dark}; accent=${2:-}
V=$([ "$variant" = dark ] && echo ObscuraDark || echo ObscuraLight)
S=${PREVIEW_DIR:-$here/build/preview}; rm -rf "$S/cfg"; mkdir -p "$S/cfg/Kvantum"
cp ~/.config/kdeglobals "$S/cfg/kdeglobals"
XDG_CONFIG_HOME=$S/cfg plasma-apply-colorscheme "$V" >/dev/null 2>&1
[ -n "$accent" ] && XDG_CONFIG_HOME=$S/cfg plasma-apply-colorscheme --accent-color "$accent" >/dev/null 2>&1
python3 "$here/tools/gen_kvantum.py" "$variant" "$S/cfg/Kvantum" "${accent:-#00aa88}" >/dev/null
printf '[General]\ntheme=%s\n' "$V" > "$S/cfg/Kvantum/kvantum.kvconfig"
XDG_CONFIG_HOME=$S/cfg QT_STYLE_OVERRIDE=kvantum QT_QPA_PLATFORMTHEME=kde python3 "$here/tools/preview_app.py" "$S/$variant${accent:+-${accent#\#}}.png"
echo "$S/$variant${accent:+-${accent#\#}}.png"
