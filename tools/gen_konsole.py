#!/usr/bin/env python3
"""Generate Konsole colour schemes (Obscura Dark / Light). Usage: gen_konsole.py [outdir]"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from palette import *

# Hues taken from the per-app accents on the site, normal + bright
ANSI = {
    "dark":  ["#1c1d22", "#ff6259", "#2fd39c", "#ffb347", "#74aaff", "#b69cff", "#52d1ea", "#f2f1ee"],
    "light": ["#101014", "#b3261e", "#007a54", "#b35f00", "#1a5bc4", "#6a3fd6", "#09596d", "#e9e8e4"],
}
BRIGHT = {
    "dark":  ["#4a4b52", "#ff8a70", "#3fe6ae", "#ffc14d", "#7fb0ff", "#c9b4ff", "#7fe0f2", "#ffffff"],
    "light": ["#4a4b52", "#e0368f", "#136938", "#8a5800", "#253e99", "#8b5cf6", "#0b6f82", "#ffffff"],
}


def scheme(v, key):
    c = lambda h: ",".join(map(str, rgb(h)))
    out = [f"[Background]\nColor={c(v['window'])}\n", f"[BackgroundIntense]\nColor={c(v['view'])}\n",
           f"[Foreground]\nColor={c(v['ink'])}\n", f"[ForegroundIntense]\nColor={c('#ffffff' if key == 'dark' else '#000000')}\n"]
    names = ["Color0", "Color1", "Color2", "Color3", "Color4", "Color5", "Color6", "Color7"]
    for i, n in enumerate(names):
        out.append(f"[{n}]\nColor={c(ANSI[key][i])}\n")
        out.append(f"[{n}Intense]\nColor={c(BRIGHT[key][i])}\n")
        out.append(f"[{n}Faint]\nColor={c(hexs(mix(rgb(ANSI[key][i]), rgb(v['window']), 0.45)))}\n")
    out.append(f"[General]\nBlur=false\nColorRandomization=false\nDescription={v['name']}\nOpacity=1\nWallpaper=\n")
    return "\n".join(out)


if __name__ == "__main__":
    d = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "build/konsole")
    d.mkdir(parents=True, exist_ok=True)
    for key, v in (("dark", DARK), ("light", LIGHT)):
        (d / f"{v['id']}.colorscheme").write_text(scheme(v, key))
        print("wrote", d / f"{v['id']}.colorscheme")
