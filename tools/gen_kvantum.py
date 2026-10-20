#!/usr/bin/env python3
"""Generate the Obscura Kvantum theme (SVG + kvconfig) for a variant and accent.

Kvantum cannot read the Qt palette for SVG fills, so the accent is baked in here.
tools/obscura-accent-sync re-runs this whenever the System Settings accent changes.
Usage: gen_kvantum.py <dark|light> <outdir> [#accent]
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from palette import *
from svgkit import Sheet, R, P

PIECES = ("topleft", "topright", "bottomleft", "bottomright", "top", "bottom", "left", "right")


def lum(t):
    f = lambda v: (v / 255) ** 2.2
    return 0.2126 * f(t[0]) + 0.7152 * f(t[1]) + 0.0722 * f(t[2])


def frame(sh, name, fill, border, bw=1, sides="tblr", top_pieces=None):
    """A flat box: interior `name` plus the 8 frame pieces. `sides` picks which edges draw."""
    sh.el(name, 8, 8, [R(0, 0, 8, 8, fill)])
    on = lambda s: border if s in sides else None
    for p in PIECES:
        col = {"topleft": on("t") if "t" in sides and "l" in sides else None,
               "topright": on("t") if "t" in sides and "r" in sides else None,
               "bottomleft": on("b") if "b" in sides and "l" in sides else None,
               "bottomright": on("b") if "b" in sides and "r" in sides else None,
               "top": on("t"), "bottom": on("b"), "left": on("l"), "right": on("r")}[p]
        horiz = p in ("top", "bottom")
        vert = p in ("left", "right")
        w = 8 if horiz else bw
        h = 8 if vert else bw
        shapes = [R(0, 0, w, h, col)]
        if p == "top" and top_pieces:
            shapes = top_pieces(w, h)
        sh.el(f"{name}-{p}", w, h, shapes)


def tabtop(fill, border, bw):
    """Tab top piece is `bw` tall: hairline on its lower edge, `fill` above."""
    return lambda w, h: [R(0, 0, w, h - 1, fill), R(0, h - 1, w, 1, border)]


def build(v, accent=DEFAULT_ACCENT):
    a = rgb(accent)
    win, ink = rgb(v["window"]), rgb(v["ink"])
    dark = v is DARK
    on_acc = rgb(v["on_accent"]) if lum(a) > 0.2 else rgb("#f2f1ee")
    H = hexs
    line = H(mix(win, ink, 0.15))
    line_hi = H(mix(win, ink, 0.40))
    muted = H(mix(win, ink, 0.60))
    ink_h, acc, acc_ink = H(ink), H(a), H(accent_ink(accent, v))
    on_h = H(on_acc)
    btn, btn_hi = v["button"], H(mix(rgb(v["button"]), ink, 0.07))
    view, window, alt = v["view"], v["window"], v["window_alt"]
    tip = v["tooltip"]
    acc_dim = H(mix(win, a, 0.20))
    sh = Sheet()

    # ---- buttons, tool buttons, line edits, frames ----
    frame(sh, "button-normal", btn, line)
    frame(sh, "button-focused", btn_hi, line_hi)
    frame(sh, "button-pressed", acc, acc)
    frame(sh, "button-toggled", acc, acc)
    frame(sh, "tbutton-normal", None, None)
    frame(sh, "tbutton-focused", btn, line_hi)
    frame(sh, "tbutton-pressed", acc, acc)
    frame(sh, "tbutton-toggled", acc_dim, acc)
    frame(sh, "lineedit-normal", view, line_hi)
    frame(sh, "lineedit-focused", view, acc)
    frame(sh, "common-normal", None, line)
    frame(sh, "common-focused", None, line_hi)
    frame(sh, "group-normal", None, line)
    frame(sh, "menu-normal", tip, line_hi)
    frame(sh, "tooltip-normal", tip, line_hi)
    frame(sh, "dock-normal", window, line)

    # ---- item views / menu items ----
    frame(sh, "itemview-focused", H(mix(rgb(view), a, 0.14)), None)
    frame(sh, "itemview-pressed", H(mix(rgb(view), a, 0.28)), None)
    frame(sh, "itemview-toggled", acc, None)
    frame(sh, "menuitem-pressed", acc, None)
    frame(sh, "menuitem-toggled", acc, None)
    frame(sh, "menuitem-focused", acc, None)
    frame(sh, "menubaritem-pressed", acc, None)
    frame(sh, "menubaritem-focused", btn, None)
    frame(sh, "menubaritem-toggled", acc, None)
    sh.el("menuitem-left-focused", 4, 4, [R(0, 0, 4, 4, acc)])
    sh.el("menuitem-right-focused", 4, 4, [R(0, 0, 4, 4, acc)])

    # ---- tabs: selected tab carries a 2px accent cap ----
    for nm, f, b in (("tab-normal", H(mix(win, rgb("#000000"), 0.25) if dark else mix(win, ink, 0.05)), line),
                     ("tab-focused", btn, line_hi),
                     ("tab-toggled", window, line),
                     ("floating-tab-normal", None, line),
                     ("floating-tab-focused", btn, line_hi),
                     ("floating-tab-toggled", window, line)):
        frame(sh, nm, f, b, top_pieces=(lambda w, h: [R(0, 0, w, h, acc)]) if nm.endswith("toggled") else tabtop(f, b, 2))
    frame(sh, "tabframe-normal", None, line)
    sh.el("tab-tear", 8, 8, [R(0, 0, 8, 8, line_hi)])
    sh.el("header-separator", 2, 8, [R(0, 0, 1, 8, line)])
    for st, f in (("normal", alt), ("focused", btn), ("pressed", btn_hi), ("toggled", alt)):
        frame(sh, f"header-{st}", f, line, sides="b")
    frame(sh, "toolbar-normal", v["header"], line, sides="b")
    sh.el("toolbar-handle", 4, 12, [R(1, 2, 2, 2, line_hi), R(1, 6, 2, 2, line_hi), R(1, 10, 2, 2, line_hi)])
    for st in ("normal", "focused", "pressed"):
        sh.el(f"titlebar-{st}" if st != "pressed" else "titlebar-pressed", 8, 8, [R(0, 0, 8, 8, v["titlebar_active"] if st == "focused" else v["titlebar_inactive"])])

    # ---- scrollbars: thin square bars, transparent frame gives the inset ----
    frame(sh, "scrollbarslider-normal", H(mix(win, ink, 0.28)), None)
    frame(sh, "scrollbarslider-focused", H(mix(win, ink, 0.45)), None)
    frame(sh, "scrollbarslider-pressed", acc, None)
    frame(sh, "scrollbargroove-normal", None, None)
    sh.el("scrollbargroove-topglow-normal", 4, 4, [])
    sh.el("scrollbargroove-bottomglow-normal", 4, 4, [])

    # ---- sliders / progress ----
    frame(sh, "slider-normal", line_hi, None)
    frame(sh, "slider-toggled", acc, None)
    for st, col in (("normal", ink_h), ("focused", acc), ("pressed", acc_ink), ("disabled", muted)):
        sh.el(f"slidercursor-{st}", 10, 18, [R(0, 0, 10, 18, col)])
    frame(sh, "progress-normal", H(mix(win, ink, 0.10)), None)
    frame(sh, "progress-pattern-normal", acc, None)
    frame(sh, "progress-pattern-disabled", line_hi, None)

    # ---- splitter / size grip ----
    for st, col in (("normal", line), ("focused", acc), ("pressed", acc)):
        sh.el(f"splitter-{st}", 4, 4, [R(0, 0, 4, 4, col)])
    sh.el("splitter-grip-normal", 16, 4, [R(0, 1, 16, 2, line_hi)])
    sh.el("splitter-grip-focused", 16, 4, [R(0, 1, 16, 2, acc)])
    sh.el("splitter-grip-pressed", 16, 4, [R(0, 1, 16, 2, acc)])
    for st, col in (("normal", line_hi), ("focused", acc)):
        sh.el(f"resize-grip-{st}", 13, 13, [P([(13, 0), (13, 13), (0, 13)], col)])

    # ---- check boxes and radios (the radio is a square with a square dot) ----
    def box(st, fill, border, mark=None, col=None):
        return [R(0, 0, 14, 14, border), R(1, 1, 12, 12, fill)] + ([mark(col)] if mark else [])
    check = lambda c: P([(2.5, 7.5), (4.5, 5.5), (6, 7), (9.5, 3), (11.5, 5), (6, 11)], c)
    dash = lambda c: R(3, 6, 8, 2, c)
    dot = lambda c: R(4, 4, 6, 6, c)
    for kind, mark in (("checkbox", check), ("radio", dot)):
        for st, border in (("normal", line_hi), ("focused", acc), ("pressed", acc)):
            sh.el(f"{kind}-{st}", 14, 14, box(st, view, border))
            sh.el(f"{kind}-checked-{st}", 14, 14, box(st, acc, acc, mark, on_h))
    for st, border in (("normal", line_hi), ("focused", acc), ("pressed", acc)):
        sh.el(f"checkbox-tristate-{st}", 14, 14, box(st, acc, acc, dash, on_h))

    # ---- arrows (solid triangles) and spin +/- ----
    tri = {"up": [(0, 6), (6, 0), (12, 6)], "down": [(0, 0), (12, 0), (6, 6)],
           "left": [(6, 0), (6, 12), (0, 6)], "right": [(0, 0), (0, 12), (6, 6)]}
    for d, pts in tri.items():
        for st, col in (("normal", H(mix(win, ink, 0.75))), ("focused", ink_h), ("pressed", ink_h), ("disabled", line_hi)):
            sh.el(f"arrow-{d}-{st}", 12, 12, [P(pts, col)])
    for st, col in (("normal", H(mix(win, ink, 0.75))), ("pressed", ink_h)):
        sh.el(f"arrow-plus-{st}", 12, 12, [R(1, 5, 10, 2, col), R(5, 1, 2, 10, col)])
        sh.el(f"arrow-minus-{st}", 12, 12, [R(1, 5, 10, 2, col)])

    # ---- dial (octagon: nothing round here) ----
    oct_ = [(5, 0), (15, 0), (20, 5), (20, 15), (15, 20), (5, 20), (0, 15), (0, 5)]
    sh.el("dial", 20, 20, [P(oct_, btn), P([(6, 2), (14, 2), (18, 6), (18, 14), (14, 18), (6, 18), (2, 14), (2, 6)], line)])
    sh.el("dial-handle", 6, 6, [R(0, 0, 6, 6, acc)])
    sh.el("dial-notches", 20, 20, [])

    kv = kvconfig(v, a, on_acc, line, line_hi)
    return sh.svg(), kv


def kvconfig(v, a, on_acc, line, line_hi):
    ink, on = hexs(rgb(v["ink"])), hexs(on_acc)

    def sec(name, **kw):
        body = "\n".join(f"{k.replace('_', '.') if k.startswith(('frame_', 'text_', 'interior_', 'indicator_')) else k}={val}" for k, val in kw.items())
        return f"[{name}]\n{body}\n"

    fr = lambda n: dict(frame="true", frame_element=n, frame_top=1, frame_bottom=1, frame_left=1, frame_right=1)
    g = """[%General]
author=Obscura
comment=Sharp-cornered theme with an editorial look. Generated by tools/gen_kvantum.py.
x11drag=menubar_and_primary_toolbar
alt_mnemonic=true
left_tabs=true
attach_active_tab=true
mirror_doc_tabs=false
group_toolbar_buttons=false
toolbar_item_spacing=2
toolbar_interior_spacing=4
spread_progressbar=false
composite=true
menu_shadow_depth=0
tooltip_shadow_depth=0
splitter_width=4
scroll_width=9
scroll_arrows=false
scroll_min_extent=40
slider_width=2
slider_handle_width=10
slider_handle_length=18
tickless_slider_handle_size=18
check_size=14
textless_progressbar=true
progressbar_thickness=4
menubar_mouse_tracking=true
toolbutton_style=0
click_behavior=0
translucent_windows=false
blurring=false
popup_blurring=false
vertical_spin_indicators=false
spin_button_width=22
fill_rubberband=true
small_icon_size=16
large_icon_size=32
button_icon_size=16
toolbar_icon_size=22
combo_as_lineedit=false
animate_states=true
combo_menu=true
hide_combo_checkboxes=true
combo_focus_rect=false
groupbox_top_label=true
inline_spin_indicators=true
joined_inactive_tabs=false
layout_spacing=6
layout_margin=8
scrollbar_in_view=true
transient_scrollbar=false
transient_groove=false
submenu_overlap=0
tooltip_delay=-1
tree_branch_line=true
no_window_pattern=true
reduce_window_opacity=0
respect_DE=true
"""
    c = lambda t: hexs(t)
    win, vink = rgb(v["window"]), rgb(v["ink"])
    gc = f"""[GeneralColors]
window.color={v['window']}
base.color={v['view']}
alt.base.color={v['view_alt']}
button.color={v['button']}
light.color={c(mix(win, vink, 0.12))}
mid.light.color={c(mix(win, vink, 0.08))}
dark.color={c(mix(win, rgb('#000000'), 0.5))}
mid.color={c(mix(win, vink, 0.05))}
highlight.color={c(a)}
inactive.highlight.color={c(mix(a, win, 0.5))}
text.color={ink}
window.text.color={ink}
button.text.color={ink}
disabled.text.color={c(mix(win, vink, 0.4))}
tooltip.text.color={ink}
highlight.text.color={on}
link.color={c(accent_ink(hexs(a), v))}
link.visited.color={v['visited']}
"""
    parts = [g, gc, "[Hacks]\ntransparent_ktitle_label=true\nkcapacitybar_as_progressbar=true\n"]
    parts.append(sec("PanelButtonCommand", **fr("button"), interior="true", interior_element="button", indicator_element="arrow", indicator_size=9,
                     text_normal_color=ink, text_focus_color=ink, text_press_color=on, text_toggle_color=on,
                     text_margin=1, text_iconspacing=4, text_margin_top=4, text_margin_bottom=4, text_margin_left=8, text_margin_right=8))
    parts.append(sec("PanelButtonTool", **fr("tbutton"), interior="true", interior_element="tbutton",
                     text_normal_color=ink, text_focus_color=ink, text_press_color=on, text_toggle_color=ink,
                     text_margin_top=3, text_margin_bottom=3, text_margin_left=4, text_margin_right=4))
    parts.append(sec("Dock", **fr("dock"), interior="true", interior_element="dock"))
    parts.append(sec("DockTitle", frame="false", interior="false", text_focus_color=ink))
    parts.append(sec("IndicatorSpinBox", indicator_element="arrow", indicator_size=9, frame="false"))
    parts.append(sec("RadioButton", interior_element="radio", frame="false", interior="true"))
    parts.append(sec("CheckBox", interior_element="checkbox", frame="false", interior="true"))
    parts.append(sec("GenericFrame", **fr("common"), interior="false"))
    parts.append(sec("LineEdit", **fr("lineedit"), interior="true", interior_element="lineedit",
                     text_margin_left=4, text_margin_right=4, text_margin_top=3, text_margin_bottom=3))
    parts.append(sec("DropDownButton", indicator_element="arrow-down", frame="false"))
    parts.append(sec("IndicatorArrow", indicator_element="arrow", indicator_size=9, frame="false"))
    parts.append(sec("ToolboxTab", frame="false", text_normal_color=ink, text_focus_color=ink))
    parts.append(sec("Tab", **{**fr("tab"), "frame_top": 2}, interior="true", interior_element="tab", indicator_element="tab",
                     text_normal_color=ink, text_focus_color=ink, text_toggle_color=ink, text_press_color=ink,
                     text_margin_left=6, text_margin_right=6, text_margin_top=3, text_margin_bottom=3, min_width="+8"))
    parts.append(sec("TabFrame", **fr("tabframe"), interior="false"))
    parts.append(sec("TreeExpander", indicator_size=9, indicator_element="arrow"))
    parts.append(sec("HeaderSection", **{**fr("header"), "frame_top": 0, "frame_left": 0, "frame_right": 0}, interior="true", interior_element="header",
                     text_normal_color=ink, text_margin_left=6, text_margin_right=6, text_margin_top=3, text_margin_bottom=3))
    parts.append(sec("SizeGrip", indicator_element="resize-grip", indicator_size=13))
    parts.append(sec("Toolbar", **{**fr("toolbar"), "frame_top": 0, "frame_left": 0, "frame_right": 0}, interior="true", interior_element="toolbar",
                     indicator_element="toolbar", indicator_size=5))
    parts.append(sec("Slider", **{**fr("slider"), "frame_top": 0, "frame_bottom": 0, "frame_left": 0, "frame_right": 0}, interior="true", interior_element="slider"))
    parts.append(sec("SliderCursor", interior="true", interior_element="slidercursor", frame="false"))
    parts.append(sec("Progressbar", **{**fr("progress"), "frame_top": 0, "frame_bottom": 0, "frame_left": 0, "frame_right": 0}, interior="true", interior_element="progress",
                     text_normal_color=ink, text_focus_color=ink, text_press_color=ink, text_toggle_color=ink))
    parts.append(sec("ProgressbarContents", **{**fr("progress-pattern"), "frame_top": 0, "frame_bottom": 0, "frame_left": 0, "frame_right": 0}, interior="true", interior_element="progress-pattern"))
    parts.append(sec("ItemView", **fr("itemview"), interior="true", interior_element="itemview",
                     text_normal_color=ink, text_focus_color=ink, text_press_color=on, text_toggle_color=on,
                     text_margin_left=3, text_margin_right=3, text_margin_top=2, text_margin_bottom=2))
    parts.append(sec("Splitter", frame="false", interior="true", interior_element="splitter", indicator_element="splitter-grip", indicator_size=16))
    parts.append(sec("Scrollbar", indicator_size=9, indicator_element="arrow"))
    parts.append(sec("ScrollbarSlider", **{**fr("scrollbarslider"), "frame_top": 2, "frame_bottom": 2, "frame_left": 2, "frame_right": 2}, interior="true", interior_element="scrollbarslider"))
    parts.append(sec("ScrollbarGroove", frame="false", interior="true", interior_element="scrollbargroove"))
    parts.append(sec("MenuItem", **fr("menuitem"), interior="true", interior_element="menuitem", indicator_element="menuitem",
                     text_normal_color=ink, text_focus_color=on, text_press_color=on, text_toggle_color=on,
                     text_margin_left=6, text_margin_right=6, text_margin_top=3, text_margin_bottom=3))
    parts.append(sec("MenuBarItem", **fr("menubaritem"), interior="true", interior_element="menubaritem",
                     text_normal_color=ink, text_focus_color=ink, text_press_color=on, text_toggle_color=on,
                     text_margin_left=8, text_margin_right=8, text_margin_top=3, text_margin_bottom=3))
    parts.append(sec("TitleBar", frame="false", interior="true", interior_element="titlebar", indicator_size=12,
                     text_normal_color=ink, text_focus_color=ink))
    parts.append(sec("ComboBox", frame="true", frame_element="button", interior="true", interior_element="button",
                     frame_top=1, frame_bottom=1, frame_left=1, frame_right=1,
                     text_margin_left=8, text_margin_right=4, text_margin_top=3, text_margin_bottom=3))
    parts.append(sec("Menu", **fr("menu"), interior="true", interior_element="menu", text_normal_color=ink))
    parts.append(sec("GroupBox", **fr("group"), interior="false", text_margin_top=2, text_margin_left=6, text_margin_right=6, text_margin_bottom=2))
    parts.append(sec("ToolTip", **fr("tooltip"), interior="true", interior_element="tooltip",
                     text_normal_color=ink, text_margin_left=6, text_margin_right=6, text_margin_top=4, text_margin_bottom=4))
    parts.append(sec("StatusBar", frame="false", interior="false"))
    parts.append(sec("Window", interior="false", frame="false"))
    return "\n".join(parts)


def write(variant, outdir, accent=DEFAULT_ACCENT):
    v = DARK if variant == "dark" else LIGHT
    name = v["id"].replace(" ", "")
    d = pathlib.Path(outdir) / name
    d.mkdir(parents=True, exist_ok=True)
    svg, kv = build(v, accent)
    (d / f"{name}.svg").write_text(svg)
    (d / f"{name}.kvconfig").write_text(kv)
    return d


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "build/Kvantum")
    acc = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_ACCENT
    variants = ["dark", "light"] if sys.argv[1] == "both" else [sys.argv[1]]
    for var in variants:
        print("wrote", write(var, out, acc))
