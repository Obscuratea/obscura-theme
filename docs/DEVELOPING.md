# Developing Obscura

Nothing in the theme is hand-drawn: each layer is generated from `tools/palette.py` so every layer stays consistent
and the dark and light variants can't drift apart.

## Layout

```
install.sh / uninstall.sh      installer (with first-run backup) and the matching revert
tools/palette.py               single source of truth: colors, default accent
tools/svgkit.py                tiny SVG sheet builder shared by the generators
tools/gen_colors.py            KDE color schemes
tools/gen_plasma.py            Plasma style (ColorScheme-* classes, so Plasma recolors it live)
tools/gen_kvantum.py           Kvantum theme (SVG + kvconfig), accent baked in
tools/gen_aurorae.py           window decorations (Aurorae SVG), accent baked in
tools/gen_cursors.py           cursors: SVG polygons rendered with Qt, written as XCursor
tools/gen_lookandfeel.py       Global Themes + splash screen
tools/gen_wallpaper.py, gen_konsole.py
tools/apply_gtk.py             marked CSS block for GTK3/4 + libadwaita color mapping
tools/obscura-accent-sync      the accent-sync program (installed to ~/.local/bin)
systemd/                       its user service and path unit
tools/preview.sh               renders a Qt widget gallery against a scratch config
```

## Build without installing

```bash
python3 tools/gen_colors.py build/color-schemes
python3 tools/gen_kvantum.py both build/Kvantum '#8b5cf6'   # try another accent
tools/preview.sh dark '#e8573f'                             # -> build/preview/dark-e8573f.png
```

`tools/preview.sh` uses a scratch `XDG_CONFIG_HOME`, so it never touches your real settings. Run `tools/check-deps.sh`
first if a generator complains about a missing module.

## How the accent follows

Three mechanisms, depending on what a layer can read:

1. **Reads the palette itself** (Plasma style, color scheme, Qt Quick, the splash, GTK via kde-gtk-config): follows for free.
2. **Colors baked into SVG** (Kvantum, Aurorae): `obscura-accent-sync` regenerates them. A systemd user path unit watches
   `~/.config/kdeglobals` and `~/.config/kdedefaults/kdeglobals`.
3. **Cursors**: also regenerated, but KDE only reloads cursors when the cursor-theme *setting* changes, so the sync builds
   the new accent into an idle copy (`Obscura-Cursors` / `Obscura-Cursors-2`) and switches to it.

## Gotchas found the hard way

- **Read config with `kreadconfig6`, not by parsing `kdeglobals`.** A Global Theme writes the color scheme and widget style
  to `~/.config/kdedefaults/kdeglobals`, which the raw file doesn't contain.
- **The exact accent is `[Colors:View] DecorationFocus`.** `[Colors:Selection] BackgroundNormal` is darkened by KDE for contrast.
- **`plasma-apply-colorscheme <current scheme>` is a no-op.** To reset an accent, switch to another scheme and back.
- **Global Themes cannot set fonts**; that's why `tools/apply-fonts.sh` exists.
- **KDE's cursor tools only scan `~/.icons`**, not `~/.local/share/icons`.
- **Kvantum without a `[GeneralColors]` section** resets the view background to white, so the generator always writes it.
- **Plasma Login Manager's greeter QML is compiled into the binary**, so it can't be themed like SDDM.
- Never `pkill -f` a pattern that also appears in your own command line.

## Taking screenshots

`spectacle -b -n -a -o file.png` captures the focused window (with decorations). It does not draw the mouse pointer.
Crop captures tightly, and check them for personal content before committing.

## Ideas

A custom sharp icon set, a custom lock screen, an editor (Kate) theme, an automated accent-sync test.
