#!/usr/bin/env bash
# Check everything Obscura needs and say how to install what's missing.
# Exit status 0 = ready, 1 = something required is missing.
here=$(cd "$(dirname "$0")" && pwd)
missing=0; cmds=()

need() { # need <command> [why]
    if command -v "$1" >/dev/null 2>&1; then printf '  ok       %s\n' "$1"
    else printf '  MISSING  %-30s %s\n' "$1" "${2:-}"; missing=1; cmds+=("$1"); fi
}

echo "Obscura requirements"
echo "Commands:"
need python3                    "Python 3.9 or newer"
need kreadconfig6               "part of KDE Frameworks (kconfig)"
need kwriteconfig6              "part of KDE Frameworks (kconfig)"
need qdbus6                     "Qt 6 tools"
need plasma-apply-colorscheme   "part of plasma-workspace"
need plasma-apply-desktoptheme  "part of plasma-workspace"
need plasma-apply-cursortheme   "part of plasma-workspace"
need plasma-apply-lookandfeel   "part of plasma-workspace"
need kvantummanager             "the Kvantum Qt style, Qt 6 build"
need systemctl                  "systemd (for the accent-sync user service)"
need curl                       "downloads the fonts"
need fc-cache                   "fontconfig"
need dbus-send                  "D-Bus"

echo "Python modules:"
for m in "PIL:python-pillow (wallpapers)" "PySide6.QtSvg:PySide6 with QtSvg (cursors)"; do
    mod=${m%%:*}
    if python3 -c "import $mod" 2>/dev/null; then printf '  ok       %s\n' "$mod"
    else printf '  MISSING  %-30s %s\n' "$mod" "${m#*:}"; missing=1; fi
done

echo "Plasma version:"
if command -v plasmashell >/dev/null 2>&1; then
    v=$(plasmashell --version 2>/dev/null | awk '{print $2}')
    case "$v" in
        6.*) printf '  ok       Plasma %s\n' "$v" ;;
        *)   printf '  MISSING  Plasma 6 (found: %s). Obscura needs Plasma 6.\n' "${v:-unknown}"; missing=1 ;;
    esac
else printf '  MISSING  plasmashell (is KDE Plasma installed?)\n'; missing=1; fi

echo "Recommended (a warning only):"
if [ -d /usr/share/themes/Breeze ] || [ -d ~/.local/share/themes/Breeze ]; then printf '  ok       Breeze GTK theme\n'
else printf '  warning  Breeze GTK theme not found: GTK apps will not follow the palette (package: breeze-gtk / gtk-breeze)\n'; fi

if [ "$missing" = 1 ]; then
    . /etc/os-release 2>/dev/null
    echo; echo "Install the missing pieces (distro: ${PRETTY_NAME:-unknown}):"
    case " ${ID:-} ${ID_LIKE:-} " in
        *" arch "*)    echo "  sudo pacman -S --needed plasma-desktop breeze-gtk kvantum python-pillow pyside6 qt6-tools curl fontconfig" ;;
        *fedora*)      echo "  sudo dnf install kvantum python3-pillow python3-pyside6 qt6-qttools curl fontconfig   # package names not tested by the author" ;;
        *suse*)        echo "  sudo zypper install kvantum-qt6 python3-Pillow python3-pyside6 qt6-tools curl fontconfig   # package names not tested by the author" ;;
        *debian*|*ubuntu*) echo "  sudo apt install qt6-style-kvantum python3-pil python3-pyside6.qtsvg qt6-base-dev-tools curl fontconfig   # package names not tested by the author" ;;
        *)             echo "  Install whatever provides the missing commands above on your distro." ;;
    esac
    echo "  (Package names outside Arch/CachyOS are best effort: search your package manager for the command or module name.)"
    exit 1
fi
echo; echo "All requirements met."
