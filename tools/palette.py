"""Single source of truth for the Obscura theme. Every generator imports this."""

def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def hexs(t):
    return "#%02x%02x%02x" % tuple(t)

def mix(a, b, t):
    """t=0 -> a, t=1 -> b"""
    return tuple(round(x * (1 - t) + y * t) for x, y in zip(a, b))

# CachyOS logo green. Used when no accent is chosen in System Settings.
DEFAULT_ACCENT = "#00aa88"

# Surface/ink tokens, from a warm editorial web palette.
DARK = dict(
    name="Obscura Dark", id="ObscuraDark",
    window="#121316", window_alt="#18191d",
    button="#1c1d22", view="#0b0b0e", view_alt="#101014",
    header="#101014", tooltip="#1c1d22",
    ink="#f2f1ee", on_accent="#101014",
    negative="#ff6259", neutral="#ffb347", positive="#2fd39c", visited="#b69cff",
    titlebar_active="#101014", titlebar_inactive="#121316",
    muted=0.60,
)
LIGHT = dict(
    name="Obscura Light", id="ObscuraLight",
    window="#f2f1ee", window_alt="#e9e8e4",
    button="#e9e8e4", view="#faf9f7", view_alt="#f2f1ee",
    header="#e9e8e4", tooltip="#faf9f7",
    ink="#101014", on_accent="#101014",
    negative="#b3261e", neutral="#b35f00", positive="#007a54", visited="#6a3fd6",
    titlebar_active="#faf9f7", titlebar_inactive="#f2f1ee",
    muted=0.60,
)

def accent_ink(accent, variant):
    """Accent tuned for text/links: lighter on dark, darker on light."""
    a = rgb(accent)
    return mix(a, (255, 255, 255), 0.35) if variant is DARK else mix(a, (0, 0, 0), 0.38)
