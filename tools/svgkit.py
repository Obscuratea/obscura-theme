"""Tiny SVG sheet builder shared by the generators.

Every element is a <g id> holding an invisible rect so its bounding box stays fixed
(Kvantum and KSvg both scale an element's bbox into the target rect)."""


class Sheet:
    def __init__(self, width=900, style=""):
        self.out, self.x, self.y, self.row_h, self.width, self.style = [], 0, 0, 0, width, style

    def el(self, eid, w, h, shapes):
        if self.x + w > self.width:
            self.x, self.y, self.row_h = 0, self.y + self.row_h + 4, 0
        ox, oy = self.x, self.y
        body = "".join(s(ox, oy) for s in shapes)
        self.out.append(f'<g id="{eid}"><rect x="{ox}" y="{oy}" width="{w}" height="{h}" fill="#000" fill-opacity="0"/>{body}</g>')
        self.x += w + 4
        self.row_h = max(self.row_h, h)

    def svg(self):
        defs = f"<defs>{self.style}</defs>\n" if self.style else ""
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.y + self.row_h}">\n'
                + defs + "\n".join(self.out) + "\n</svg>\n")


def R(x, y, w, h, fill=None, op=1, cls=None):
    """Rect. `cls` paints with a ColorScheme-* class (Plasma recolours these from the live palette)."""
    if fill is None and cls is None:
        return lambda ox, oy: ""
    a = f' fill-opacity="{op}"' if op != 1 else ""
    paint = f'class="{cls}" fill="currentColor"' if cls else f'fill="{fill}"'
    return lambda ox, oy: f'<rect x="{ox + x}" y="{oy + y}" width="{w}" height="{h}" {paint}{a} shape-rendering="crispEdges"/>'


def P(pts, fill=None, op=1, cls=None):
    a = f' fill-opacity="{op}"' if op != 1 else ""
    paint = f'class="{cls}" fill="currentColor"' if cls else f'fill="{fill}"'

    def f(ox, oy):
        s = " ".join(f"{ox + a_},{oy + b}" for a_, b in pts)
        return f'<polygon points="{s}" {paint}{a}/>'
    return f
