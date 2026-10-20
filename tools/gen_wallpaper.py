#!/usr/bin/env python3
"""Generate the Obscura wallpaper package: dark in images_dark/, light in images/.
Plasma picks the right one for the active colour scheme.
Usage: gen_wallpaper.py [outdir]
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from PIL import Image, ImageDraw, ImageFont
from palette import *

FONTS = pathlib.Path.home() / ".local/share/fonts/obscura"
SIZES = [(3440, 1440), (2560, 1440), (3840, 2160), (1440, 2560), (1920, 1080)]


def face(name, size, variation=None):
    f = ImageFont.truetype(str(FONTS / name), size)
    if variation:
        try:
            f.set_variation_by_name(variation)
        except Exception:
            pass
    return f


def render(v, w, h):
    win, ink, acc = rgb(v["window"]), rgb(v["ink"]), rgb(DEFAULT_ACCENT)
    im = Image.new("RGB", (w, h), win)
    s = min(w, h) / 1440  # scale all measurements to the short edge
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)

    # hairline grid, and a faint scanline texture like the site's
    step = round(160 * s)
    for x in range(0, w, step):
        d.line([(x, 0), (x, h)], fill=(*ink, 14), width=1)
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=(*ink, 14), width=1)
    for y in range(0, h, 4):
        d.line([(0, y), (w, y)], fill=(*ink, 3), width=1)

    # crop marks
    m, L = round(64 * s), round(48 * s)
    for cx, cy, sx, sy in ((m, m, 1, 1), (w - m, m, -1, 1), (m, h - m, 1, -1), (w - m, h - m, -1, -1)):
        d.line([(cx, cy), (cx + sx * L, cy)], fill=(*ink, 90), width=2)
        d.line([(cx, cy), (cx, cy + sy * L)], fill=(*ink, 90), width=2)

    # oversized wordmark, barely there
    big = face("Archivo[wdth,wght].ttf", round(300 * s), "ExtraBold")
    d.text((m * 2, h - m * 2 - round(60 * s)), "OBSCURA", font=big, fill=(*ink, 12), anchor="ls")

    # mono labels
    mono = face("GeistMono[wght].ttf", round(22 * s), "Regular")
    d.text((m * 2, m * 2), "01 / OBSCURA", font=mono, fill=(*ink, 150), anchor="la")
    d.text((w - m * 2, m * 2), "CACHYOS · KDE PLASMA", font=mono, fill=(*ink, 90), anchor="ra")
    sq = round(14 * s)
    d.rectangle([w - m * 2 - sq, h - m * 2 - sq, w - m * 2, h - m * 2], fill=(*acc, 255))

    im.paste(lay, (0, 0), lay)
    return im


def write(root):
    root = pathlib.Path(root) / "Obscura"
    for sub, v in (("images_dark", DARK), ("images", LIGHT)):
        (root / "contents" / sub).mkdir(parents=True, exist_ok=True)
        for w, h in SIZES:
            render(v, w, h).save(root / "contents" / sub / f"{w}x{h}.png", optimize=True)
    meta = {"KPackageStructure": "Wallpaper/Images",
            "KPlugin": {"Authors": [{"Name": "Obscura"}], "Id": "Obscura", "License": "MIT", "Name": "Obscura"}}
    (root / "metadata.json").write_text(json.dumps(meta, indent=4) + "\n")
    print("wrote", root)


if __name__ == "__main__":
    write(sys.argv[1] if len(sys.argv) > 1 else "build/wallpapers")
