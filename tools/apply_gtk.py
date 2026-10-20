#!/usr/bin/env python3
"""Square off GTK apps and tie libadwaita to the live KDE palette.

kde-gtk-config already writes ~/.config/gtk-N.0/colors.css from the active scheme (accent included).
We add a clearly marked block to each gtk.css and leave everything else in the file alone.
Usage: apply_gtk.py install | remove | theme
"""
import pathlib, re, subprocess, sys

CFG = pathlib.Path.home() / ".config"
BEGIN, END = "/* >>> obscura */", "/* <<< obscura */"

SQUARE = """* { border-radius: 0; }
"""

# libadwaita reads these names; point them at the colours kde-gtk-config generates, so GTK4/libadwaita
# apps follow the Obscura scheme and the System Settings accent.
ADWAITA = """@define-color accent_bg_color @theme_selected_bg_color_breeze;
@define-color accent_fg_color @theme_selected_fg_color_breeze;
@define-color accent_color @link_color_breeze;
@define-color window_bg_color @theme_bg_color_breeze;
@define-color window_fg_color @theme_fg_color_breeze;
@define-color view_bg_color @theme_base_color_breeze;
@define-color view_fg_color @theme_text_color_breeze;
@define-color headerbar_bg_color @theme_bg_color_breeze;
@define-color headerbar_fg_color @theme_fg_color_breeze;
@define-color headerbar_border_color @borders_breeze;
@define-color card_bg_color @theme_button_background_normal_breeze;
@define-color card_fg_color @theme_button_foreground_normal_breeze;
@define-color dialog_bg_color @theme_bg_color_breeze;
@define-color dialog_fg_color @theme_fg_color_breeze;
@define-color sidebar_bg_color @theme_bg_color_breeze;
@define-color sidebar_fg_color @theme_fg_color_breeze;
@define-color popover_bg_color @tooltip_background_breeze;
@define-color popover_fg_color @tooltip_text_breeze;
@define-color destructive_bg_color @error_color_breeze;
@define-color error_color @error_color_breeze;
@define-color success_color @success_color_breeze;
@define-color warning_color @warning_color_breeze;
"""


def strip(text):
    return re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", "", text, flags=re.S)


def edit(path, block):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = strip(path.read_text() if path.exists() else "")
    if text and not text.endswith("\n"):
        text += "\n"
    path.write_text(text + (f"{BEGIN}\n{block}{END}\n" if block else ""))


def main(cmd):
    if cmd == "install":
        # the @import colors.css line (if present) must stay first so our names resolve
        edit(CFG / "gtk-3.0/gtk.css", SQUARE)
        edit(CFG / "gtk-4.0/gtk.css", ADWAITA + SQUARE)
    elif cmd == "remove":
        for v in ("3.0", "4.0"):
            p = CFG / f"gtk-{v}/gtk.css"
            if p.exists():
                edit(p, "")
    elif cmd == "theme":
        for v in ("3.0", "4.0"):
            subprocess.run(["kwriteconfig6", "--file", str(CFG / f"gtk-{v}/settings.ini"), "--group", "Settings",
                            "--key", "gtk-theme-name", "Breeze"], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", "Breeze"], check=False)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
