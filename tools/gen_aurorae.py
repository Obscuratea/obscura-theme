#!/usr/bin/env python3
"""Generate the Obscura Aurorae window decoration (SVG) for a variant and accent.

Aurorae SVG cannot read the palette, so the accent bar is baked in here;
tools/obscura-accent-sync re-runs this when the System Settings accent changes.
Usage: gen_aurorae.py <dark|light|both> <outdir> [#accent]
"""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from palette import *
from svgkit import Sheet, R, P

# Title bar: 2px accent cap + 25px bar + 1px hairline = 28px. Buttons fill the 25px bar.
TITLE_H, CAP, BW = 28, 2, 1
BTN_W, BTN_H = 32, 25


def glyphs(ink):
    """Button glyphs drawn in a BTN_W x BTN_H box, as (ox, oy) -> svg callables."""
    cx, cy = BTN_W / 2, BTN_H / 2

    def stroke(x1, y1, x2, y2, w=1.4):
        # a diagonal line as a thin quad, so nothing is round
        import math
        dx, dy = x2 - x1, y2 - y1
        n = math.hypot(dx, dy) or 1
        ox, oy = -dy / n * w / 2, dx / n * w / 2
        return [(x1 + ox, y1 + oy), (x2 + ox, y2 + oy), (x2 - ox, y2 - oy), (x1 - ox, y1 - oy)]

    def poly(pts): return P(pts, ink)

    return {
        "close": [poly(stroke(cx - 5, cy - 5, cx + 5, cy + 5)), poly(stroke(cx - 5, cy + 5, cx + 5, cy - 5))],
        "minimize": [R(cx - 5, cy + 1, 10, 1, ink)],
        "maximize": [R(cx - 5, cy - 5, 10, 1, ink), R(cx - 5, cy + 4, 10, 1, ink), R(cx - 5, cy - 5, 1, 10, ink), R(cx + 4, cy - 5, 1, 10, ink)],
        "restore": [R(cx - 3, cy - 5, 8, 1, ink), R(cx + 4, cy - 5, 1, 7, ink), R(cx - 5, cy - 3, 8, 1, ink),
                    R(cx - 5, cy + 4, 8, 1, ink), R(cx - 5, cy - 3, 1, 8, ink), R(cx + 2, cy - 3, 1, 8, ink)],
        "alldesktops": [R(cx - 3, cy - 3, 6, 6, ink)],
        "keepabove": [poly([(cx - 5, cy + 3), (cx, cy - 3), (cx + 5, cy + 3)]), R(cx - 5, cy - 5, 10, 1, ink)],
        "keepbelow": [poly([(cx - 5, cy - 3), (cx, cy + 3), (cx + 5, cy - 3)]), R(cx - 5, cy + 4, 10, 1, ink)],
        "shade": [R(cx - 5, cy - 4, 10, 2, ink)],
    }


def button_svg(kind, v):
    win, ink = rgb(v["window"]), rgb(v["ink"])
    tb_act, tb_in = v["titlebar_active"], v["titlebar_inactive"]
    states = {
        # state: (background, glyph colour)
        "active": (None, hexs(mix(rgb(tb_act), ink, 0.75))),
        "inactive": (None, hexs(mix(rgb(tb_in), ink, 0.40))),
        "deactivated": (None, hexs(mix(rgb(tb_act), ink, 0.22))),
        "hover": (hexs(mix(rgb(tb_act), ink, 0.12)), hexs(ink)),
        "pressed": (hexs(mix(rgb(tb_act), ink, 0.22)), hexs(ink)),
    }
    if kind == "close":
        neg = rgb(v["negative"])
        states["hover"] = (hexs(neg), "#ffffff")
        states["pressed"] = (hexs(mix(neg, (0, 0, 0), 0.25)), "#ffffff")
    sh = Sheet(width=BTN_W * 5 + 40)
    for st, (bg, col) in states.items():
        shapes = ([R(0, 0, BTN_W, BTN_H, bg)] if bg else []) + glyphs(col)[kind]
        sh.el(f"{st}-center", BTN_W, BTN_H, shapes)
    return sh.svg()


def decoration_svg(v, accent):
    win, ink = rgb(v["window"]), rgb(v["ink"])
    a = hexs(rgb(accent))
    line = hexs(mix(win, ink, 0.18))
    sh = Sheet(width=200)
    for tag, bar, tb in (("", a, v["titlebar_active"]), ("inactive-", None, v["titlebar_inactive"])):
        p = lambda n: f"decoration-{tag}{n}"
        edge = lambda: [R(0, 0, 8, 8, line)]
        # bar pieces: 2px cap, bar, 1px hairline underneath, all inside TITLE_H
        def titlebar(w):
            top = [R(0, 0, w, CAP, bar)] if bar else [R(0, 0, w, CAP, tb)]
            return [R(0, 0, w, TITLE_H, tb)] + top + [R(0, TITLE_H - 1, w, 1, line)]
        sh.el(p("top"), 8, TITLE_H, titlebar(8) + [R(0, 0, 8, 1, bar or line)])
        sh.el(p("topleft"), BW, TITLE_H, titlebar(BW) + [R(0, 0, BW, TITLE_H, line)] + ([R(0, 0, BW, CAP, bar)] if bar else []))
        sh.el(p("topright"), BW, TITLE_H, titlebar(BW) + [R(0, 0, BW, TITLE_H, line)] + ([R(0, 0, BW, CAP, bar)] if bar else []))
        sh.el(p("left"), BW, 8, [R(0, 0, BW, 8, line)])
        sh.el(p("right"), BW, 8, [R(0, 0, BW, 8, line)])
        sh.el(p("bottom"), 8, BW, [R(0, 0, 8, BW, line)])
        sh.el(p("bottomleft"), BW, BW, [R(0, 0, BW, BW, line)])
        sh.el(p("bottomright"), BW, BW, [R(0, 0, BW, BW, line)])
        sh.el(p("center"), 8, 8, [R(0, 0, 8, 8, v["window"])])
    for side, (w, h) in {"top": (4, TITLE_H), "bottom": (4, BW), "left": (BW, 4), "right": (BW, 4)}.items():
        sh.el(f"hint-{side}-margin", w, h, [])
    return sh.svg()


RC = """[General]
ActiveTextColor={act}
InactiveTextColor={inact}
TitleAlignment=Left
TitleVerticalAlignment=Center
UseTextShadow=false
LeftButtons=M
RightButtons=IAX
Shadow=false
Animation=0

[Layout]
BorderLeft={bw}
BorderRight={bw}
BorderBottom={bw}
TitleEdgeTop={cap}
TitleEdgeBottom={eb}
TitleEdgeLeft=8
TitleEdgeRight=0
TitleBorderLeft=8
TitleBorderRight=8
TitleHeight={bar}
ButtonWidth={bw_}
ButtonHeight={bh}
ButtonSpacing=0
ButtonMarginTop=0
ButtonMarginLeft=0
ExplicitButtonSpacer=0
PaddingTop=0
PaddingBottom=0
PaddingRight=0
PaddingLeft=0
TitleEdgeTopMaximized={cap}
TitleEdgeBottomMaximized={eb}
TitleEdgeLeftMaximized=8
TitleEdgeRightMaximized=0
"""


def write(variant, outdir, accent=DEFAULT_ACCENT):
    v = DARK if variant == "dark" else LIGHT
    name = v["id"]
    d = pathlib.Path(outdir) / name
    d.mkdir(parents=True, exist_ok=True)
    win, ink = rgb(v["window"]), rgb(v["ink"])
    (d / "decoration.svg").write_text(decoration_svg(v, accent))
    for kind in ("close", "maximize", "restore", "minimize", "alldesktops", "keepabove", "keepbelow", "shade"):
        (d / f"{kind}.svg").write_text(button_svg(kind, v))
    c = lambda t: ",".join(str(x) for x in t)
    (d / f"{name}rc").write_text(RC.format(act=c(ink), inact=c(mix(win, ink, 0.55)), bw=BW, cap=CAP,
                                          eb=TITLE_H - CAP - 25, bar=25, bw_=BTN_W, bh=BTN_H))
    meta = {"KPackageStructure": "KWin/Aurorae",
            "KPlugin": {"Authors": [{"Name": "Obscura"}], "Category": "Plasma 6 Window Decorations",
                        "ServiceTypes": ["KWin/Aurorae"], "EnabledByDefault": True,
                        "Name": v["name"], "Description": "Sharp window decorations with an editorial look",
                        "Id": name, "Version": "0.1", "License": "MIT",
                        "X-KDE-PluginInfo-blur": False}}
    (d / "metadata.json").write_text(json.dumps(meta, indent=4) + "\n")
    (d / "metadata.desktop").write_text(f"[Desktop Entry]\nName={v['name']}\nComment=Sharp window decorations\nX-KDE-PluginInfo-Name={name}\nX-KDE-PluginInfo-Version=0.1\nX-KDE-PluginInfo-License=MIT\nX-KDE-ServiceTypes=KWin/Decoration\n")
    return d


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "build/aurorae")
    acc = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_ACCENT
    for var in (["dark", "light"] if sys.argv[1] == "both" else [sys.argv[1]]):
        print("wrote", write(var, out, acc))
