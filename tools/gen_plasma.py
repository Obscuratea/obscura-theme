#!/usr/bin/env python3
"""Generate the Obscura Plasma style (desktoptheme).

Colours are ColorScheme-* classes, so Plasma recolours them from the active palette:
the accent, and dark/light, follow System Settings with no regeneration.
Anything not generated here falls back to Plasma's default theme.
Usage: gen_plasma.py [outdir]
"""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from palette import *
from svgkit import Sheet, R, P

PIECES = ("topleft", "topright", "bottomleft", "bottomright", "top", "bottom", "left", "right")

# Defaults only matter when an SVG is rendered outside Plasma; Plasma overwrites these per palette.
_D = DARK
STYLE = '<style type="text/css" id="current-color-scheme">' + "".join(
    f".ColorScheme-{n}{{color:{c};}}" for n, c in {
        "Text": _D["ink"], "Background": _D["window"], "Highlight": DEFAULT_ACCENT, "HighlightedText": _D["on_accent"],
        "ViewText": _D["ink"], "ViewBackground": _D["view"], "ViewHover": DEFAULT_ACCENT, "ViewFocus": DEFAULT_ACCENT,
        "ButtonText": _D["ink"], "ButtonBackground": _D["button"], "ButtonHover": DEFAULT_ACCENT, "ButtonFocus": DEFAULT_ACCENT,
        "NegativeText": _D["negative"], "NeutralText": _D["neutral"], "PositiveText": _D["positive"],
    }.items()) + "</style>"

# (class, opacity) paint tokens
TEXT = "ColorScheme-Text"
BG, BTN, VIEW = "ColorScheme-Background", "ColorScheme-ButtonBackground", "ColorScheme-ViewBackground"
ACC, ACC_V, ACC_B = "ColorScheme-Highlight", "ColorScheme-ViewFocus", "ColorScheme-ButtonFocus"
HOV_B, ACC_ON = "ColorScheme-ButtonHover", "ColorScheme-HighlightedText"
LINE, LINE_HI, LINE_FIELD = (TEXT, .15), (TEXT, .40), (TEXT, .30)
NEU = "ColorScheme-NeutralText"


def paint(p):
    """(class, opacity) -> kwargs for R"""
    return {} if p is None else dict(cls=p[0], op=p[1])


def px(sh, name, w, h, p):
    sh.el(name, w, h, [R(0, 0, w, h, **paint(p))])


def margins(sh, pre, t, b, l, r, kind="margin"):
    """Padding hints: top/bottom are read from a rect's height, left/right from its width."""
    z = lambda v: max(v, 0.001)
    sh.el(f"{pre}hint-top-{kind}", 4, z(t), [])
    sh.el(f"{pre}hint-bottom-{kind}", 4, z(b), [])
    sh.el(f"{pre}hint-left-{kind}", z(l), 4, [])
    sh.el(f"{pre}hint-right-{kind}", z(r), 4, [])


def nine(sh, pre, fill, border, bw=1, m=None, sides="tblr", bws=None, bcolors=None):
    """9-patch `pre`{center,top,...}. `bws` overrides border width per side; `bcolors` the colour per side."""
    bws = {"t": bw, "b": bw, "l": bw, "r": bw, **(bws or {})}
    col = {s: (bcolors or {}).get(s, border) if s in sides else None for s in "tblr"}
    px(sh, f"{pre}center", 8, 8, fill)
    for p in PIECES:
        v, h = ("t" if "top" in p else "b" if "bottom" in p else None), ("l" if "left" in p else "r" if "right" in p else None)
        if p in ("top", "bottom"):
            side, w, hh = v, 8, bws[v]
        elif p in ("left", "right"):
            side, w, hh = h, bws[h], 8
        else:  # corners take their vertical edge's colour
            side, w, hh = v, bws[h], bws[v]
        px(sh, f"{pre}{p}", w, hh, col[side])
    if m is not None:
        t, b, l, r = m if isinstance(m, tuple) else (m,) * 4
        margins(sh, pre, t, b, l, r)


def surface(sh, fill_op, border=LINE_HI, m=6, thick=False):
    nine(sh, "", (BG, fill_op), border, 1, m)
    if thick:
        px(sh, "thick-center", 32, 32, (BG, fill_op))
        margins(sh, "thick-", 4, 4, 4, 4)


def write(sh, root, rel):
    d = pathlib.Path(root) / rel
    d.parent.mkdir(parents=True, exist_ok=True)
    d.write_text(sh.svg())


# ---------------------------------------------------------------- frames
def frames(root, folder, op_dialog, op_widget, op_panel, op_tip):
    pre = f"{folder}/" if folder else ""
    for rel, op, m, thick in (("dialogs/background", op_dialog, 4, False), ("widgets/background", op_widget, 6, False),
                              ("widgets/panel-background", op_panel, 2, True), ("widgets/tooltip", op_tip, 4, False)):
        if folder == "opaque" and rel == "widgets/background":
            continue  # Plasma ships no opaque widgets/background either
        sh = Sheet(style=STYLE)
        surface(sh, op, m=m, thick=thick)
        write(sh, root, f"{pre}{rel}.svg")


# ---------------------------------------------------------------- controls
def button(root):
    sh = Sheet(style=STYLE)
    for pre, fill, bd in (("normal-", (BTN, 1), LINE), ("hover-", (BTN, 1), (HOV_B, 1)), ("focus-", (BTN, 1), (ACC_B, 1)),
                          ("pressed-", (ACC_B, .25), (ACC_B, 1)),
                          ("toolbutton-hover-", (TEXT, .07), LINE_HI), ("toolbutton-focus-", None, (ACC_B, 1)),
                          ("toolbutton-pressed-", (ACC_B, .25), (ACC_B, 1))):
        nine(sh, pre, fill, bd, 1, 6)
    write(sh, root, "widgets/button.svg")


def lineedit(root):
    sh = Sheet(style=STYLE)
    sh.el("hint-focus-over-base", 2, 2, [])
    for pre, bd in (("base-", LINE_FIELD), ("hover-", (TEXT, .55)), ("focus-", (ACC_V, 1))):
        nine(sh, pre, (VIEW, 1), bd, 1, (4, 4, 6, 6))
    nine(sh, "focusframe-", None, None, 1, 0)
    write(sh, root, "widgets/lineedit.svg")


def frame(root):
    sh = Sheet(style=STYLE)
    nine(sh, "plain-", None, LINE, 1, 4)
    nine(sh, "sunken-", (VIEW, 1), LINE, 1, 4)
    nine(sh, "raised-", (BTN, 1), LINE, 1, 4)
    write(sh, root, "widgets/frame.svg")


def tabbar(root):
    sh = Sheet(style=STYLE)
    # active tab: hairline box with a 2px accent cap on the outer edge
    for orient, cap in (("north", "t"), ("south", "b"), ("west", "l"), ("east", "r")):
        nine(sh, f"{orient}-active-tab-", (BTN, 1), LINE_HI, 1, (6, 6, 8, 8),
             bws={cap: 2}, bcolors={cap: (ACC, 1)})
    write(sh, root, "widgets/tabbar.svg")


def scrollbar(root):
    sh = Sheet(style=STYLE)
    sh.el("hint-scrollbar-size", 10, 10, [])
    for pre in ("background-vertical-", "background-horizontal-"):
        nine(sh, pre, None, None, 1)
        margins(sh, pre, 2, 2, 2, 2, "inset")
    for pre, fill in (("slider-", (TEXT, .30)), ("mouseover-slider-", (ACC, 1))):
        nine(sh, pre, fill, None, 1)
        margins(sh, pre, 2, 2, 2, 2, "inset")
    write(sh, root, "widgets/scrollbar.svg")


def slider(root):
    sh = Sheet(style=STYLE)
    sh.el("hint-tile-center", 2, 2, [])
    sh.el("hint-handle-size", 14, 14, [])
    for o in ("horizontal", "vertical"):
        for st, fill, bd in (("handle", (BTN, 1), (TEXT, .6)), ("hover", (BTN, 1), (ACC, 1)), ("focus", (ACC, 1), (ACC, 1))):
            sh.el(f"{o}-slider-{st}", 14, 14, [R(0, 0, 14, 14, **paint(bd)), R(1, 1, 12, 12, **paint(fill))])
    write(sh, root, "widgets/slider.svg")


def switch(root):
    sh = Sheet(style=STYLE)
    sh.el("hint-stretch-borders", 4, 4, [])
    sh.el("hint-bar-size", 36, 16, [])
    for st, fill, bd in (("active", (ACC, 1), (ACC, 1)), ("inactive", (TEXT, .10), LINE_HI)):
        px(sh, f"{st}-center", 8, 16, fill)
        px(sh, f"{st}-left", 1, 16, bd)
        px(sh, f"{st}-right", 1, 16, bd)
    for st, fill, bd in (("handle", (BTN, 1), (TEXT, .6)), ("handle-hover", (BTN, 1), (ACC, 1)),
                         ("handle-focus", (BTN, 1), (ACC, 1)), ("handle-pressed", (ACC_B, .25), (ACC, 1))):
        sh.el(st, 20, 20, [R(0, 0, 20, 20, **paint(bd)), R(1, 1, 18, 18, **paint(fill))])
    write(sh, root, "widgets/switch.svg")


def checks(root):
    sh = Sheet(style=STYLE)
    box = [R(0, 0, 16, 16, cls=ACC, op=1)]
    sh.el("checkbox", 16, 16, box + [P([(3, 8), (5, 6), (7, 8), (11, 4), (13, 6), (7, 12)], cls=ACC_ON)])
    sh.el("radiobutton", 16, 16, box + [R(5, 5, 6, 6, cls=ACC_ON)])
    write(sh, root, "widgets/checkmarks.svg")
    sh = Sheet(style=STYLE)
    sh.el("hint-size", 16, 16, [])
    for st, bd in (("normal", (TEXT, .4)), ("hover", (TEXT, .7)), ("focus", (ACC, 1))):
        sh.el(st, 16, 16, [R(0, 0, 16, 16, **paint(bd)), R(1, 1, 14, 14, cls=VIEW)])
    sh.el("checked", 16, 16, [R(0, 0, 16, 16, cls=ACC), R(1, 1, 14, 14, cls=VIEW), R(5, 5, 6, 6, cls=ACC)])
    write(sh, root, "widgets/radiobutton.svg")


def items(root):
    sh = Sheet(style=STYLE)
    nine(sh, "normal-", None, None, 1, 4)
    nine(sh, "hover-", (TEXT, .08), None, 1, 4)
    nine(sh, "pressed-", (ACC, .25), (ACC, 1), 1, 4)
    write(sh, root, "widgets/menubaritem.svg")

    sh = Sheet(style=STYLE)
    sh.el("hint-tile-center", 8, 8, [])
    nine(sh, "normal-", None, None, 1)
    nine(sh, "hover-", (TEXT, .08), None, 1)
    nine(sh, "selected-", (ACC, .25), (ACC, 1), 1, bcolors={"l": (ACC, 1)}, bws={"l": 2})
    nine(sh, "selected+hover-", (ACC, .35), (ACC, 1), 1, bcolors={"l": (ACC, 1)}, bws={"l": 2})
    write(sh, root, "widgets/viewitem.svg")

    sh = Sheet(style=STYLE)
    sh.el("hint-tile-center", 8, 8, [])
    sh.el("separator", 8, 1, [R(0, 0, 8, 1, cls=TEXT, op=.15)])
    nine(sh, "normal-", None, None, 1, (6, 6, 6, 6))
    nine(sh, "hover-", (TEXT, .08), None, 1)
    nine(sh, "pressed-", (ACC, .25), (ACC, 1), 1, (6, 6, 6, 6))
    nine(sh, "section-", None, None, 1, (6, 6, 6, 6))
    write(sh, root, "widgets/listitem.svg")


def bars(root):
    sh = Sheet(style=STYLE)
    sh.el("hint-tile-center", 2, 2, [])
    nine(sh, "", (BG, 1), LINE, 1, 4, sides="b")
    write(sh, root, "widgets/toolbar.svg")

    sh = Sheet(style=STYLE)
    sh.el("hint-stretch-borders", 4, 4, [])
    nine(sh, "header-", (BG, 1), LINE, 1, sides="b")
    nine(sh, "footer-", (BG, 1), LINE, 1, sides="t")
    margins(sh, "", 4, 4, 6, 6)
    write(sh, root, "widgets/plasmoidheading.svg")


def tasks(root):
    sh = Sheet(style=STYLE)
    # prefix "" = panel at the bottom; others sit the indicator bar on the side facing the screen edge
    for orient, cap in (("", "b"), ("north-", "t"), ("west-", "l"), ("east-", "r")):
        for st, fill, bar in (("normal", None, None), ("hover", (TEXT, .08), None), ("minimized", None, None),
                              ("focus", (ACC, .18), (ACC, 1)), ("attention", (NEU, .18), (NEU, 1)),
                              ("progress", (ACC, .28), None)):
            nine(sh, f"{orient}{st}-", fill, None, 1, 4 if st == "normal" and not orient else None,
                 bws={cap: 2} if bar else None, bcolors={cap: bar} if bar else None, sides=cap if bar else "")
        # normal- margins are read by the Task Manager for every orientation
        if orient:
            margins(sh, f"{orient}normal-", 4, 4, 4, 4)
    write(sh, root, "widgets/tasks.svg")


def actionbutton(root):
    sh = Sheet(style=STYLE)
    for size in ("", "16-16-", "22-22-", "24-24-"):
        n = int(size.split("-")[0]) if size else 22
        for st, fill, bd in (("normal", (BG, .6), LINE), ("hover", (BG, .6), (HOV_B, 1)),
                             ("focus", (BG, .6), (ACC_B, 1)), ("pressed", (ACC_B, .25), (ACC_B, 1))):
            sh.el(f"{size}{st}", n, n, [R(0, 0, n, n, **paint(bd)), R(1, 1, n - 2, n - 2, **paint(fill))])
    write(sh, root, "widgets/actionbutton.svg")


def metadata(root):
    meta = {
        "KPackageStructure": "Plasma/Theme",
        "KPlugin": {
            "Authors": [{"Name": "Obscura"}],
            "Category": "",
            "Description": "Sharp-cornered Plasma style with an editorial look. Follows the system accent.",
            "Id": "Obscura",
            "License": "MIT",
            "Name": "Obscura",
            "Version": "0.1",
        },
    }
    (pathlib.Path(root) / "metadata.json").write_text(json.dumps(meta, indent=4) + "\n")


def build(root):
    root = pathlib.Path(root)
    root.mkdir(parents=True, exist_ok=True)
    frames(root, "", .94, .94, .90, .96)
    frames(root, "translucent", .85, .85, .80, .90)
    frames(root, "solid", 1, 1, 1, 1)
    frames(root, "opaque", 1, 1, 1, 1)
    for fn in (button, lineedit, frame, tabbar, scrollbar, slider, switch, checks, items, bars, tasks, actionbutton):
        fn(root)
    metadata(root)


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "build/desktoptheme/Obscura")
    build(out)
    n = sum(1 for _ in out.rglob("*.svg"))
    print(f"wrote {n} svg files to {out}")
