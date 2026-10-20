#!/usr/bin/env bash
# Remove Obscura and put back the look you had before, using the snapshot install.sh took
# the first time it ran (~/.local/share/obscura/backup). Your wallpaper is not restored automatically.
set -uo pipefail
here=$(cd "$(dirname "$0")" && pwd)
b=~/.local/share/obscura/backup
[ -d "$b" ] || { echo "No backup found at $b, so there is nothing to restore from."; echo "Pick another Global Theme in System Settings, then delete the Obscura files by hand."; exit 1; }
echo "Restoring the settings saved on $(cat "$b/taken-on" 2>/dev/null || echo an earlier date)"

# Read a value as KDE would have: the user file first, then the defaults layer (~/.config/kdedefaults),
# which is where a Global Theme keeps the color scheme, Plasma style, decoration theme and so on.
rd() {
    local v
    v=$(kreadconfig6 --file "$b/$1" --group "$2" --key "$3")
    [ -z "$v" ] && v=$(kreadconfig6 --file "$b/kdedefaults/$1" --group "$2" --key "$3")
    printf '%s' "$v"
}
wr() { [ -n "$4" ] && kwriteconfig6 --file "$1" --group "$2" --key "$3" "$4"; return 0; }

systemctl --user disable --now obscura-accent-sync.path 2>/dev/null
rm -f ~/.config/systemd/user/obscura-accent-sync.{service,path} ~/.local/bin/obscura-accent-sync
rm -rf ~/.local/share/obscura/tools ~/.cache/obscura
systemctl --user daemon-reload

# the defaults layer is written only by Global Theme applies: put it back exactly as it was
[ -d "$b/kdedefaults" ] && { mkdir -p ~/.config/kdedefaults; cp -a "$b/kdedefaults/." ~/.config/kdedefaults/; }

# put the previous look back first; fall back to Plasma defaults if the backup had no explicit value
or() { [ -n "$1" ] && echo "$1" || echo "$2"; }
plasma-apply-colorscheme "$(or "$(rd kdeglobals General ColorScheme)" BreezeLight)" >/dev/null
plasma-apply-desktoptheme "$(or "$(rd plasmarc Theme name)" default)" >/dev/null
plasma-apply-cursortheme "$(or "$(rd kcminputrc Mouse cursorTheme)" breeze_cursors)" >/dev/null
kwriteconfig6 --file kdeglobals --group KDE --key widgetStyle "$(or "$(rd kdeglobals KDE widgetStyle)" Breeze)"
wr kdeglobals KDE LookAndFeelPackage "$(rd kdeglobals KDE LookAndFeelPackage)"
for k in font menuFont toolBarFont smallestReadableFont fixed; do wr kdeglobals General "$k" "$(rd kdeglobals General $k)"; done
wr kdeglobals WM activeFont "$(rd kdeglobals WM activeFont)"
for k in library theme ButtonsOnLeft ButtonsOnRight; do
    v=$(rd kwinrc org.kde.kdecoration2 $k)
    if [ -n "$v" ]; then wr kwinrc org.kde.kdecoration2 $k "$v"; else kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key $k --delete; fi
done
# no explicit decoration before means "Breeze"
[ -z "$(rd kwinrc org.kde.kdecoration2 theme)" ] && kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.breeze
wr ksplashrc KSplash Theme "$(rd ksplashrc KSplash Theme)"
kv=$(grep -m1 '^theme=' "$b/kvantum.kvconfig" 2>/dev/null | cut -d= -f2)
wr ~/.config/Kvantum/kvantum.kvconfig General theme "$kv"
gtk=$(grep -m1 '^gtk-theme-name=' "$b/gtk3-settings.ini" 2>/dev/null | cut -d= -f2)
if [ -n "$gtk" ]; then
    for v in 3.0 4.0; do wr ~/.config/gtk-$v/settings.ini Settings gtk-theme-name "$gtk"; done
    gsettings set org.gnome.desktop.interface gtk-theme "$gtk" 2>/dev/null
fi
python3 "$here/tools/apply_gtk.py" remove

dbus-send --session --type=signal /KGlobalSettings org.kde.KGlobalSettings.notifyChange int32:2 int32:0
dbus-send --session --type=signal /KGlobalSettings org.kde.KGlobalSettings.notifyChange int32:1 int32:0
qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1

rm -rf ~/.local/share/color-schemes/Obscura{Dark,Light}.colors ~/.local/share/plasma/desktoptheme/Obscura \
       ~/.local/share/plasma/look-and-feel/org.obscura.{dark,light}.desktop ~/.local/share/wallpapers/Obscura \
       ~/.local/share/aurorae/themes/Obscura{Dark,Light} ~/.config/Kvantum/Obscura{Dark,Light} \
       ~/.icons/Obscura-Cursors ~/.icons/Obscura-Cursors-2 ~/.local/share/konsole/Obscura{Dark,Light}.colorscheme
echo "Done. Left in place: the fonts (~/.local/share/fonts/obscura) and your settings snapshot (~/.local/share/obscura/backup)."
echo "Delete them by hand if you want them gone. Your wallpaper was not changed back."
