"""Glassy iOS-style weather widget.

A self-contained weather card: a golden-hour sky gradient, a big current
temperature, procedural weather icons built entirely from primitive shapes
(a rayed sun, layered-ellipse clouds, rain streaks), and a row of five
frosted-glass forecast tiles. No external assets, no network.
"""

import math
from pathlib import Path

from easy_pil import DropShadow, Editor, Font, Glow
from easy_pil.canvas import Canvas
from easy_pil.gradient import LinearGradient, RadialGradient

OUT = Path(__file__).parent / "outputs"
OUT.mkdir(exist_ok=True)

W, H = 760, 900
RADIUS = 56

# Golden-hour sky: deep steel-blue up top easing down into warm peach.
SKY = LinearGradient(
    ["#2f5d92", "#5b83b3", "#a9b5cf", "#f0b483", "#f6c98a"],
    direction="vertical",
)

SUN_CORE = RadialGradient(["#fff6cf", "#ffd45e"], center=(0.42, 0.4))
SUN_RAY = "#ffe08a"
WHITE = "#ffffff"
SOFT = "#eef3fb"
MUTED = "#dbe4f2"


def sun_icon(size, *, core=SUN_CORE, ray=SUN_RAY, rays=12, glow=True):
    """Return a transparent editor with a rayed sun drawn inset for glow room."""
    ed = Editor(Canvas((size, size), color=(0, 0, 0, 0)))
    cx = cy = size / 2
    r_core = size * 0.205
    r_in = size * 0.30
    r_out = size * 0.46
    w = max(2, int(size * 0.035))
    for i in range(rays):
        a = math.pi * 2 * i / rays
        x1, y1 = cx + math.cos(a) * r_in, cy + math.sin(a) * r_in
        x2, y2 = cx + math.cos(a) * r_out, cy + math.sin(a) * r_out
        ed.line((x1, y1), (x2, y2), width=w, fill=ray)
        ed.ellipse((x2 - w / 2, y2 - w / 2), w, w, fill=ray)
    ed.ellipse((cx - r_core, cy - r_core), r_core * 2, r_core * 2, fill=core)
    if glow:
        ed.effect(Glow(radius=int(size * 0.09), color="#ffdf87", alpha=0.55))
    return ed


def cloud_icon(size, *, body="#ffffff", shade=None):
    """Return a transparent editor with a puffy cloud from layered ellipses."""
    ed = Editor(Canvas((size, size), color=(0, 0, 0, 0)))
    if shade:
        # A soft under-shadow puff for a hint of volume.
        ed.ellipse((size * 0.18, size * 0.52), size * 0.60, size * 0.26, fill=shade)
    # Base slab plus three bumps of varying size.
    ed.rectangle(
        (size * 0.16, size * 0.52),
        size * 0.68,
        size * 0.20,
        fill=body,
        radius=int(size * 0.11),
    )
    ed.ellipse((size * 0.15, size * 0.42), size * 0.34, size * 0.34, fill=body)
    ed.ellipse((size * 0.36, size * 0.30), size * 0.44, size * 0.44, fill=body)
    ed.ellipse((size * 0.55, size * 0.44), size * 0.30, size * 0.30, fill=body)
    return ed


def partly_icon(size):
    """Return a small sun peeking from behind a cloud."""
    ed = Editor(Canvas((size, size), color=(0, 0, 0, 0)))
    sun = sun_icon(int(size * 0.62), glow=True)
    ed.paste(sun, (int(size * 0.06), int(size * 0.02)))
    ed.paste(
        cloud_icon(size, body="#f4f8ff", shade=(120, 140, 170, 60)),
        (0, int(size * 0.12)),
    )
    return ed


def rain_icon(size):
    """Return a grey cloud with a few slanted rain streaks."""
    ed = Editor(Canvas((size, size), color=(0, 0, 0, 0)))
    ed.paste(
        cloud_icon(size, body="#eaf0f8", shade=(110, 130, 165, 70)),
        (0, int(-size * 0.06)),
    )
    drop = "#7fb2e8"
    for i in range(3):
        x = size * (0.34 + i * 0.16)
        y = size * 0.70
        ed.line(
            (x, y),
            (x - size * 0.06, y + size * 0.16),
            width=max(2, int(size * 0.035)),
            fill=drop,
        )
    return ed


ICONS = {"sun": sun_icon, "partly": partly_icon, "cloud": cloud_icon, "rain": rain_icon}


def make_icon(kind, size):
    if kind == "cloud":
        return cloud_icon(size, body="#ffffff", shade=(120, 140, 170, 55))
    return ICONS[kind](size)


# ---------------------------------------------------------------- build card
card = Editor(Canvas((W, H), color=SKY))

# Soft top sheen to sell the glassy, backlit sky.
sheen = Editor(Canvas((W, 260), color=(0, 0, 0, 0)))
sheen.rectangle((0, 0), W, 260, fill=(255, 255, 255, 40))
sheen.blur("gaussian", 60)
card.paste(sheen, (0, -40), opacity=0.6)

# Hero sun, top-right, with its own drop shadow for a lifted feel.
hero = sun_icon(300, rays=12, glow=True)
card.paste(hero, (W - 320, 8))

# ---- header text
card.text(
    (56, 58),
    "San Francisco",
    font=Font.poppins(variant="bold", size=46),
    color=WHITE,
)
card.text(
    (58, 122),
    "Monday, July 6",
    font=Font.poppins(variant="light", size=25),
    color=MUTED,
)

# ---- current conditions
card.text(
    (46, 224),
    "72°",
    font=Font.poppins(variant="bold", size=190),
    color=WHITE,
)
card.text(
    (60, 440),
    "Mostly Sunny",
    font=Font.poppins(variant="bold", size=40),
    color=SOFT,
)
card.text(
    (62, 500),
    "Feels like 74°",
    font=Font.poppins(variant="regular", size=26),
    color=MUTED,
)
# H/L tucked under the sun to balance the right column.
card.text(
    (W - 60, 396),
    "H: 75°",
    font=Font.poppins(variant="bold", size=30),
    color=WHITE,
    anchor="rm",
)
card.text(
    (W - 60, 442),
    "L: 58°",
    font=Font.poppins(variant="regular", size=30),
    color=MUTED,
    anchor="rm",
)

# ---------------------------------------------------------------- forecast
FC_TOP = 590
PANEL_H = H - FC_TOP - 38
MARGIN = 40

# One wide frosted-glass panel behind the tiles (built translucent, pasted).
panel = Editor(Canvas((W - MARGIN * 2, PANEL_H), color=(0, 0, 0, 0)))
panel.rectangle(
    (0, 0),
    W - MARGIN * 2 - 1,
    PANEL_H - 1,
    fill=(255, 255, 255, 38),
    radius=40,
    outline=(255, 255, 255, 70),
    stroke_width=2,
)
card.paste(panel, (MARGIN, FC_TOP))

card.text(
    (MARGIN + 28, FC_TOP + 26),
    "5-DAY FORECAST",
    font=Font.poppins(variant="bold", size=19),
    color=SOFT,
)
card.line(
    (MARGIN + 28, FC_TOP + 66),
    (W - MARGIN - 28, FC_TOP + 66),
    width=2,
    fill=(255, 255, 255, 60),
)

days = [
    ("Mon", "sun", "75°"),
    ("Tue", "partly", "73°"),
    ("Wed", "cloud", "68°"),
    ("Thu", "rain", "70°"),
    ("Fri", "partly", "66°"),
]

tiles_top = FC_TOP + 90
tiles_h = PANEL_H - 90 - 24
usable = W - MARGIN * 2 - 40
gap = 14
tile_w = (usable - gap * (len(days) - 1)) / len(days)
start_x = MARGIN + 20

for i, (label, kind, temp) in enumerate(days):
    tx = start_x + i * (tile_w + gap)
    # Frosted mini-tile.
    tile = Editor(Canvas((int(tile_w), int(tiles_h)), color=(0, 0, 0, 0)))
    tile.rectangle(
        (0, 0),
        int(tile_w) - 1,
        int(tiles_h) - 1,
        fill=(255, 255, 255, 46),
        radius=28,
        outline=(255, 255, 255, 60),
        stroke_width=2,
    )
    card.paste(tile, (int(tx), tiles_top))

    cx = tx + tile_w / 2
    label_y = tiles_top + 26
    temp_y = tiles_top + tiles_h - 28
    # Day label
    card.text(
        (cx, label_y),
        label,
        font=Font.poppins(variant="bold", size=22),
        color=WHITE,
        anchor="mm",
    )
    # Icon centered in the band between label and temp (no overlap).
    isz = int(min(tile_w * 0.58, (temp_y - label_y) - 46))
    icon = make_icon(kind, isz)
    icon_cy = (label_y + temp_y) / 2 + 4
    card.paste(icon, (int(cx - isz / 2), int(icon_cy - isz / 2)))
    # Temp
    card.text(
        (cx, temp_y),
        temp,
        font=Font.poppins(variant="bold", size=26),
        color=SOFT,
        anchor="mm",
    )

# ---------------------------------------------------------------- finish
card.rounded_corners(radius=RADIUS)

# Lift the whole widget off a neutral backdrop with a soft shadow.
pad = 60
frame = Editor(Canvas((W + pad * 2, H + pad * 2), color="#0e1420"))
shadowed = Editor(Canvas((W + pad * 2, H + pad * 2), color=(0, 0, 0, 0)))
shadowed.paste(card, (pad, pad))
shadowed.effect(DropShadow(offset=(0, 26), blur_radius=46, color=(0, 0, 0), alpha=0.5))
frame.paste(shadowed, (0, 0))

frame.save(OUT / "weather_card.png")
print("saved", OUT / "weather_card.png", frame.image.size)
