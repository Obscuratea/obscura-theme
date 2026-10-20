# Installing Obscura

This guide assumes you have never installed a KDE theme from source. Every step says what it does.
If you get stuck, jump to [Troubleshooting](#troubleshooting).

## 1. What you need

**Desktop:** KDE Plasma **6**. Tested only on CachyOS with Plasma 6.8 on Wayland; other Plasma 6 versions and X11 should work but are untested. Plasma 5 will not work.
Distros that ship Plasma 5 only (for example Ubuntu 24.04 with its default desktop) are not supported.

**Software** (the installer checks all of this for you and tells you what's missing):

| What | Why | Command it provides |
|---|---|---|
| KDE Plasma 6 (`plasma-desktop`, `plasma-workspace`, `kconfig`) | the desktop itself and its `plasma-apply-*` tools | `kreadconfig6`, `plasma-apply-lookandfeel`, ... |
| Kvantum (Qt 6 build) | the Qt widget style | `kvantummanager` |
| Qt 6 tools | talks to KWin | `qdbus6` |
| Python 3.9+ with **Pillow** and **PySide6** (with QtSvg) | generates the wallpapers and cursors | `python3` |
| `curl`, `fontconfig` | downloads and registers the fonts | `curl`, `fc-cache` |
| systemd (user session) | runs the small accent-sync service | `systemctl` |
| Breeze GTK theme *(recommended)* | lets GTK apps follow the palette | folder `/usr/share/themes/Breeze` |

You also need an internet connection for the font download (about 4 MB) and under 20 MB of disk.

**Install the packages**

Arch, CachyOS, Manjaro, EndeavourOS:

```bash
sudo pacman -S --needed plasma-desktop breeze-gtk kvantum python-pillow pyside6 qt6-tools curl fontconfig
```

Other distros (package names are best effort and **not tested by the author**; if one isn't found, search your
package manager for the command or module name in the table above):

```bash
# Fedora
sudo dnf install kvantum python3-pillow python3-pyside6 qt6-qttools curl fontconfig
# openSUSE
sudo zypper install kvantum-qt6 python3-Pillow python3-pyside6 qt6-tools curl fontconfig
# Debian / Ubuntu / Kubuntu (Plasma 6 releases only)
sudo apt install qt6-style-kvantum python3-pil python3-pyside6.qtsvg qt6-base-dev-tools curl fontconfig
```

On these distros also install the package that provides the **Breeze GTK theme** (often named `breeze-gtk` or `breeze-gtk-theme`).

## 2. Get the theme

Open a terminal (in KDE: press `Meta` (the Windows key), type **Konsole**, press Enter), then:

```bash
git clone https://github.com/Obscuratea/obscura-theme.git
cd obscura-theme
```

No git? Click **Code → Download ZIP** on the GitHub page, unzip it, open a terminal in the folder, and carry on.

## 3. Check your requirements (optional but recommended)

```bash
./tools/check-deps.sh
```

It prints `ok` or `MISSING` for each requirement and, for anything missing, the command to install it. Fix those
first; the installer runs the same check and refuses to continue if something required is absent.

## 4. Install

```bash
./install.sh
```

What happens, in order:

1. Checks your requirements.
2. **Saves your current appearance settings** to `~/.local/share/obscura/backup` (only the first time).
   This is what `./uninstall.sh` restores later.
3. Downloads the fonts into `~/.local/share/fonts/obscura`.
4. Generates the theme files and copies them into your home folder.
5. Starts the accent-sync background service.

It never uses `sudo` and never writes outside your home directory. It is safe to run again.

Want it to also switch you to the theme straight away? Use `./install.sh --apply` instead.

## 5. Switch to Obscura

If you didn't use `--apply`:

1. Open **System Settings → Appearance & Style → Global Theme**.
2. Pick **Obscura Dark** (or **Obscura Light**) and apply it.
3. If you see an option to use the theme's *desktop layout*, leave it off. That keeps your own panels and widgets.

The Global Theme sets the colors, Plasma style, Qt style, window decorations, cursors, splash screen and wallpaper.
Switching between Obscura Dark and Light later flips everything together.

## 6. Fonts, GTK apps and extras

Global Themes can't change fonts, so apply them yourself. This keeps your current font size:

```bash
./tools/apply-fonts.sh               # or: SIZE=10 ./tools/apply-fonts.sh
python3 tools/apply_gtk.py theme     # makes GTK apps use the Breeze GTK theme so they follow the palette
```

(`./install.sh --apply` already ran both.) Log out and back in, or restart apps, for fonts to fully take effect.

Optional:

- **Konsole:** Settings → Edit Current Profile → Appearance → choose *Obscura Dark* or *Obscura Light*.
- **Wallpaper:** the Global Theme sets it. Otherwise right-click the desktop → Configure Desktop and Wallpaper → *Obscura*.
  Plasma shows the dark or light image to match your color scheme.

## 7. Change the accent color

Open **System Settings → Colors**. The row of colored dots at the top is the accent picker.

- Pick a dot (or the eyedropper) to set your accent.
- Choose **Accent color from color scheme** to go back to Obscura's default, CachyOS green `#00aa88`.

Plasma follows instantly. Qt apps, window title bars, and cursors update a few seconds later, because a background
service rebuilds them. Apps that were already open may keep the old cursor until you restart them.

## Updating

```bash
cd obscura-theme
git pull
./install.sh
```

Your accent and dark/light choice are kept.

## Uninstalling

```bash
./uninstall.sh
```

This switches back to the appearance you had before (from the snapshot saved in step 4), stops the service, and
removes the Obscura files. It leaves behind the fonts and the snapshot folder; delete
`~/.local/share/fonts/obscura` and `~/.local/share/obscura` yourself if you want those gone. It does **not** restore
your old wallpaper: pick it again in the desktop settings.

## What the installer changes

Everything is in your home directory:

| Where | What |
|---|---|
| `~/.local/share/color-schemes`, `plasma/desktoptheme`, `plasma/look-and-feel`, `wallpapers`, `aurorae/themes`, `konsole` | the theme files |
| `~/.config/Kvantum/ObscuraDark`, `ObscuraLight` | the Qt style |
| `~/.icons/Obscura-Cursors` (and `-2`) | cursors (two copies so cursor changes register; see DEVELOPING.md) |
| `~/.config/gtk-3.0/gtk.css`, `gtk-4.0/gtk.css` | one clearly marked `obscura` block each; the rest of those files is untouched |
| `~/.local/bin/obscura-accent-sync`, `~/.local/share/obscura/tools` | the accent-sync program |
| `~/.config/systemd/user/obscura-accent-sync.{service,path}` | runs the sync when your colors change |
| `~/.local/share/fonts/obscura` | the downloaded fonts |
| `~/.local/share/obscura/backup` | your settings snapshot |

## Troubleshooting

**The installer says something is MISSING.** Install it with the command it prints, then run `./install.sh` again.

**"Obscura" isn't in the Global Theme list.** Run `./install.sh` again and check for errors. Then reopen System Settings.
Make sure you are on Plasma 6 (`plasmashell --version`).

**Qt apps still look like Breeze or look unstyled.** Open **System Settings → Appearance & Style → Application Style**
and make sure the widget style is **kvantum**. Applying the Global Theme sets it; changing the theme in the Application
Style page can undo it.

**The accent doesn't change in Qt apps, window borders or cursors.**
Check the service: `systemctl --user status obscura-accent-sync.path` should say *active (waiting)*. If not:
`systemctl --user enable --now obscura-accent-sync.path`. You can force a rebuild any time with
`~/.local/bin/obscura-accent-sync --force`. The sync only acts while an Obscura color scheme is active.

**Some app still has the old cursor.** Restart that app. XWayland and GTK apps load cursors when they start.

**Text isn't in the Obscura fonts.** Run `tools/apply-fonts.sh`, then log out and in. Check the fonts are visible with
`fc-list | grep -i -E 'archivo|geist|instrument'`. If the list is empty, run `tools/install-fonts.sh`.

**GTK apps don't follow the palette.** Install the Breeze GTK theme (`breeze-gtk` on Arch) and run
`python3 tools/apply_gtk.py theme`. Flatpak apps are sandboxed and may not see your Qt style or GTK settings; that is a
general Flatpak limitation and Obscura has not been tested with them.

**Something looks wrong and I want my old setup back.** Run `./uninstall.sh`.

**It doesn't work on my setup.** Please open an issue and include: your distro, `plasmashell --version`, whether you use
Wayland or X11 (`echo $XDG_SESSION_TYPE`), and the output of `./tools/check-deps.sh`.
