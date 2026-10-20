#!/usr/bin/env bash
# Build and install Obscura into your user profile. No root needed. Safe to run again.
#
#   ./install.sh             install; switch themes yourself in System Settings
#   ./install.sh --apply     install and switch to Obscura Dark (also sets fonts and the GTK theme)
#   ./install.sh --no-fonts  skip the font download
#
# The first run saves your current appearance settings to ~/.local/share/obscura/backup,
# which ./uninstall.sh uses to put everything back.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
cd "$here"

apply=0; fonts=1
for a in "$@"; do
    case "$a" in
        --apply) apply=1 ;;
        --no-fonts) fonts=0 ;;
        -h|--help) sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "unknown option: $a (try --help)" >&2; exit 2 ;;
    esac
done

tools/check-deps.sh || { echo; echo "Install the missing requirements above, then run ./install.sh again."; exit 1; }
echo

# ---- one-time backup of the settings Obscura changes ----
state=~/.local/share/obscura; bk=$state/backup
if [ ! -d "$bk" ]; then
    echo "Saving your current appearance settings to $bk"
    mkdir -p "$bk"
    cp_if() { [ -e "$1" ] && cp -r "$1" "$bk/$2" || true; }
    cp_if ~/.config/kdeglobals kdeglobals
    cp_if ~/.config/kdedefaults kdedefaults
    cp_if ~/.config/kwinrc kwinrc
    cp_if ~/.config/plasmarc plasmarc
    cp_if ~/.config/kcminputrc kcminputrc
    cp_if ~/.config/ksplashrc ksplashrc
    cp_if ~/.config/Kvantum/kvantum.kvconfig kvantum.kvconfig
    cp_if ~/.config/gtk-3.0/settings.ini gtk3-settings.ini
    cp_if ~/.config/gtk-3.0/gtk.css gtk3.css
    cp_if ~/.config/gtk-4.0/gtk.css gtk4.css
    cp_if ~/.config/plasma-org.kde.plasma.desktop-appletsrc plasma-org.kde.plasma.desktop-appletsrc
    date -I > "$bk/taken-on"
fi

[ "$fonts" = 1 ] && { echo "Fonts"; tools/install-fonts.sh; echo; }

echo "Building"
python3 tools/gen_colors.py build/color-schemes >/dev/null
python3 tools/gen_kvantum.py both build/Kvantum >/dev/null
python3 tools/gen_plasma.py build/desktoptheme/Obscura >/dev/null
python3 tools/gen_aurorae.py both build/aurorae >/dev/null
python3 tools/gen_lookandfeel.py build/look-and-feel >/dev/null
python3 tools/gen_wallpaper.py build/wallpapers >/dev/null
python3 tools/gen_konsole.py build/konsole >/dev/null
rm -rf build/cursors build/cursor-svg
python3 tools/gen_cursors.py build/cursors '#00aa88' --svg-dir build/cursor-svg >/dev/null

echo "Installing"
mkdir -p ~/.local/share/{color-schemes,plasma/desktoptheme,plasma/look-and-feel,wallpapers,konsole,aurorae/themes} ~/.config/Kvantum ~/.icons
cp build/color-schemes/*.colors ~/.local/share/color-schemes/
rm -rf ~/.local/share/plasma/desktoptheme/Obscura
cp -r build/desktoptheme/Obscura ~/.local/share/plasma/desktoptheme/Obscura
for v in ObscuraDark ObscuraLight; do
    rm -rf ~/.config/Kvantum/$v ~/.local/share/aurorae/themes/$v
    cp -r build/Kvantum/$v ~/.config/Kvantum/$v
    cp -r build/aurorae/$v ~/.local/share/aurorae/themes/$v
done
for v in dark light; do
    rm -rf ~/.local/share/plasma/look-and-feel/org.obscura.$v.desktop
    cp -r build/look-and-feel/org.obscura.$v.desktop ~/.local/share/plasma/look-and-feel/
done
rm -rf ~/.local/share/wallpapers/Obscura; cp -r build/wallpapers/Obscura ~/.local/share/wallpapers/
cp build/konsole/*.colorscheme ~/.local/share/konsole/
# KDE's cursor tools only look in ~/.icons, not ~/.local/share/icons
rm -rf ~/.icons/Obscura-Cursors; cp -a build/cursors/Obscura-Cursors ~/.icons/
python3 tools/apply_gtk.py install

# Accent sync: the generators are installed beside the script so it keeps working without this checkout.
mkdir -p ~/.local/bin "$state/tools" ~/.config/systemd/user
cp tools/palette.py tools/svgkit.py tools/gen_kvantum.py tools/gen_aurorae.py tools/gen_cursors.py "$state/tools/"
install -m755 tools/obscura-accent-sync ~/.local/bin/obscura-accent-sync
cp systemd/obscura-accent-sync.{service,path} ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now obscura-accent-sync.path >/dev/null 2>&1 || echo "note: could not enable the accent-sync service (no systemd user session?)"

# Match Kvantum / window decorations / cursors to the accent you have right now (does nothing unless an Obscura scheme is active)
~/.local/bin/obscura-accent-sync --force || true

if [ "$apply" = 1 ]; then
    echo "Applying Obscura Dark"
    plasma-apply-lookandfeel -a org.obscura.dark.desktop
    tools/apply-fonts.sh
    python3 tools/apply_gtk.py theme
fi

echo
echo "Installed. Next: System Settings > Appearance > Global Theme > Obscura Dark (or Obscura Light)."
echo "Then run tools/apply-fonts.sh for the Obscura fonts, and see docs/INSTALL.md for the rest."
