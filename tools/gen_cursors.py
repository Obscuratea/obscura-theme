#!/usr/bin/env python3
"""Generate the Obscura cursor theme: SVG source -> XCursor at 24/32/48/64.

Every shape is a sharp polygon: dark fill, mitered accent border, 1px dark outer edge.
Each size is rendered from the vector, never resampled. Cursors are static files, so
tools/obscura-accent-sync re-runs this when the System Settings accent changes.

Usage: gen_cursors.py <outdir> [#accent] [--svg-dir DIR]
"""
import math, os, pathlib, struct, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from palette import DEFAULT_ACCENT, DARK, rgb, hexs, mix

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QByteArray
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

SIZES = (24, 32, 48, 64)
GRID = 32
FILL, EDGE, DANGER = "#101014", "#000000", "#ff6259"


# ------------------------------------------------------------------ drawing
def poly(pts, stroke, fill=None, sw=1.9, halo=True):
    """A sharp shape: 1px dark halo outside, then the coloured border, then the fill."""
    d = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    base = f'points="{d}" stroke-linejoin="miter" stroke-miterlimit="10"'
    out = ""
    if halo:
        out += f'<polygon {base} fill="{EDGE}" fill-opacity=".55" stroke="{EDGE}" stroke-opacity=".55" stroke-width="{sw + 2:.2f}"/>'
    return out + f'<polygon {base} fill="{fill or FILL}" stroke="{stroke}" stroke-width="{sw:.2f}"/>'


def rot(pts, deg, cx=16, cy=16):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def scale(pts, k, cx=0, cy=0):
    return [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in pts]


def shift(pts, dx, dy):
    return [(x + dx, y + dy) for x, y in pts]


DART = [(3, 3), (25, 12.5), (14.5, 15.5), (11.5, 26.5)]  # tip, wing, notch, tail
TRI_UP = [(16, 3), (24, 13), (8, 13)]


def dart(a, fill=None, stroke=None):
    return poly(DART, stroke or a, fill)


def badge(a, glyph):
    """Small accent square at the lower right of the dart, with a dark glyph."""
    box = [(17, 17), (30, 17), (30, 30), (17, 30)]
    g = {
        "plus": '<path d="M23.5 20 V27 M20 23.5 H27" stroke="%s" stroke-width="2" fill="none"/>' % FILL,
        "help": '<path d="M20.5 21.5 V20.5 H26.5 V24.5 H23.5 V26.2" stroke="%s" stroke-width="1.8" fill="none" stroke-linejoin="miter"/>'
                '<rect x="22.7" y="27.2" width="1.6" height="1.6" fill="%s"/>' % (FILL, FILL),
        "alias": '<polygon points="20,27 20,20.5 26.5,27" fill="%s"/>' % FILL,
        "menu": '<path d="M20 21 H27 M20 23.5 H27 M20 26 H27" stroke="%s" stroke-width="1.5" fill="none"/>' % FILL,
    }[glyph]
    return poly(box, FILL, a, sw=1.4) + g


def arrow_pair(a, angle=0):
    up = [(16, 2.5), (24, 12.5), (8, 12.5)]
    dn = [(16, 29.5), (24, 19.5), (8, 19.5)]
    return poly(rot(up, angle), a) + poly(rot(dn, angle), a)


def cursors(a):
    """name -> (svg body, hotspot x, hotspot y, frames). frames: list of bodies for animations."""
    c = {}
    c["default"] = (dart(a), 3, 3)
    c["pointer"] = (dart(a, fill=a, stroke=FILL), 3, 3)
    c["help"] = (dart(a) + badge(a, "help"), 3, 3)
    c["copy"] = (dart(a) + badge(a, "plus"), 3, 3)
    c["alias"] = (dart(a) + badge(a, "alias"), 3, 3)
    c["context-menu"] = (dart(a) + badge(a, "menu"), 3, 3)

    ibeam = [(11, 3), (21, 3), (21, 6), (17.5, 6), (17.5, 26), (21, 26), (21, 29), (11, 29), (11, 26), (14.5, 26), (14.5, 6), (11, 6)]
    c["text"] = (poly(ibeam, a), 16, 16)
    c["vertical-text"] = (poly(rot(ibeam, 90), a), 16, 16)

    arms = [[(13.8, 2.5), (18.2, 2.5), (16, 12.5)], [(29.5, 13.8), (29.5, 18.2), (19.5, 16)],
            [(13.8, 29.5), (18.2, 29.5), (16, 19.5)], [(2.5, 13.8), (2.5, 18.2), (12.5, 16)]]
    c["crosshair"] = ("".join(poly(p, a) for p in arms) + poly([(14.6, 14.6), (17.4, 14.6), (17.4, 17.4), (14.6, 17.4)], a, sw=1.2, halo=False), 16, 16)
    c["cell"] = c["crosshair"]

    c["ns-resize"] = (arrow_pair(a, 0), 16, 16)
    c["ew-resize"] = (arrow_pair(a, 90), 16, 16)
    c["nesw-resize"] = (arrow_pair(a, 45), 16, 16)
    c["nwse-resize"] = (arrow_pair(a, -45), 16, 16)

    small = [(16, 2.5), (21.5, 10), (10.5, 10)]
    c["move"] = ("".join(poly(rot(small, r), a) for r in (0, 90, 180, 270))
                 + poly([(13.8, 13.8), (18.2, 13.8), (18.2, 18.2), (13.8, 18.2)], a, sw=1.2, halo=False), 16, 16)

    up = [(16, 2.5), (25, 14), (19, 14), (19, 29.5), (13, 29.5), (13, 14), (7, 14)]
    c["up-arrow"] = (poly(up, a), 16, 3)

    pen = [(3, 29.5), (5.5, 20), (21, 4.5), (27.5, 11), (12, 26.5)]
    c["pencil"] = (poly(pen, a) + poly([(3, 29.5), (5.5, 20), (12, 26.5)], a, sw=1.2, halo=False), 3, 29)

    diamond = [(16, 2.5), (29.5, 16), (16, 29.5), (2.5, 16)]
    c["not-allowed"] = (poly(diamond, DANGER) + poly([(9.5, 12), (12, 9.5), (22.5, 20), (20, 22.5)], DANGER, DANGER, sw=1, halo=False), 16, 16)

    # wait: one isosceles triangle spinning about the centre
    def spinner(k=1.0, off=(0, 0), phase=0):
        tri = [(16, 4), (24.5, 25), (7.5, 25)]
        return poly(shift(scale(rot(tri, phase), k, 16, 16), *off), a)
    n = 24
    wait_frames = [spinner(1.0, (0, 0), i * 360 / n) for i in range(n)]
    prog_frames = [dart(a) + poly(shift(scale(rot([(16, 4), (24.5, 25), (7.5, 25)], i * 360 / n), .42, 16, 16), 7.5, 7.5), a, sw=1.4) for i in range(n)]
    c["wait"] = (wait_frames[0], 16, 16, wait_frames)
    c["progress"] = (prog_frames[0], 3, 3, prog_frames)
    return c


# names KDE / GTK / Chromium / Firefox look cursors up by
ALIASES = {
    "default": ["left_ptr", "arrow", "top_left_arrow", "dnd-ask", "color-picker", "zoom-in", "zoom-out", "left_ptr_help_alt"],
    "pointer": ["pointing_hand", "hand1", "hand2", "link"],
    "help": ["question_arrow", "whats_this", "left_ptr_help"],
    "copy": ["dnd-copy"],
    "alias": ["dnd-link"],
    "text": ["xterm", "ibeam"],
    "crosshair": ["cross", "tcross"],
    "pencil": ["draw-pencil"],
    "not-allowed": ["crossed_circle", "forbidden", "no-drop", "dnd-no-drop", "circle"],
    "ns-resize": ["size_ver", "v_double_arrow", "row-resize", "split_v", "n-resize", "s-resize", "top_side", "bottom_side", "sb_v_double_arrow", "double_arrow"],
    "ew-resize": ["size_hor", "h_double_arrow", "col-resize", "split_h", "e-resize", "w-resize", "left_side", "right_side", "sb_h_double_arrow"],
    "nwse-resize": ["size_fdiag", "nw-resize", "se-resize", "top_left_corner", "bottom_right_corner"],
    "nesw-resize": ["size_bdiag", "ne-resize", "sw-resize", "top_right_corner", "bottom_left_corner"],
    "move": ["all-scroll", "fleur", "size_all", "grabbing", "closedhand", "dnd-move", "dnd-none", "openhand", "grab"],
    "up-arrow": ["center_ptr"],
    "progress": ["left_ptr_watch", "half-busy"],
    "wait": ["watch"],
}


# ------------------------------------------------------------------ output
def svg_doc(body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{GRID}" height="{GRID}" viewBox="0 0 {GRID} {GRID}">{body}</svg>'


_app = None


def render(body, size):
    """SVG body -> premultiplied ARGB bytes at size x size."""
    global _app
    _app = _app or QGuiApplication.instance() or QGuiApplication([])
    r = QSvgRenderer(QByteArray(svg_doc(body).encode()))
    img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(0)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    r.render(p)
    p.end()
    return bytes(img.constBits())[: size * size * 4]


def xcursor(frames, hot, delay):
    chunks = []
    for size in SIZES:
        hx, hy = round(hot[0] * size / GRID), round(hot[1] * size / GRID)
        for body in frames:
            chunks.append((size, struct.pack("<IIIIIIIII", 36, 0xfffd0002, size, 1, size, size, hx, hy, delay) + render(body, size)))
    off = 16 + 12 * len(chunks)
    toc, blob = b"", b""
    for size, ch in chunks:
        toc += struct.pack("<III", 0xfffd0002, size, off)
        blob += ch
        off += len(ch)
    return b"Xcur" + struct.pack("<III", 16, 0x10000, len(chunks)) + toc + blob


def write(outdir, accent=DEFAULT_ACCENT, svg_dir=None, name="Obscura-Cursors"):
    root = pathlib.Path(outdir) / name
    cdir = root / "cursors"
    cdir.mkdir(parents=True, exist_ok=True)
    for stale in cdir.iterdir():
        stale.unlink()
    for cname, spec in cursors(accent).items():
        body, hx, hy = spec[:3]
        frames = spec[3] if len(spec) > 3 else [body]
        (cdir / cname).write_bytes(xcursor(frames, (hx, hy), 40 if len(frames) > 1 else 0))
        for alias in ALIASES.get(cname, []):
            (cdir / alias).symlink_to(cname)
        if svg_dir:
            pathlib.Path(svg_dir).mkdir(parents=True, exist_ok=True)
            (pathlib.Path(svg_dir) / f"{cname}.svg").write_text(svg_doc(body))
    (root / "index.theme").write_text(f"[Icon Theme]\nName={name}\nComment=Obscura cursors: sharp, accent-edged\nInherits=hicolor\n")
    return root


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    svg = sys.argv[sys.argv.index("--svg-dir") + 1] if "--svg-dir" in sys.argv else None
    if svg:
        args.remove(svg)
    print("wrote", write(args[0], args[1] if len(args) > 1 else DEFAULT_ACCENT, svg))
