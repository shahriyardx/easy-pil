"""Crypto price ticker card.

A sleek fintech / trading-app style card: a procedural coin badge, the coin
name and ticker, the big current price, a green/red change pill with a
directional arrow, and a smooth Catmull-Rom sparkline over the recent price
trend with a soft gradient area fill and glow. Fully self-contained — the
price series is a fixed list, no randomness, no network, no external assets.
"""

from pathlib import Path

from PIL import Image as PilImage
from PIL import ImageChops, ImageDraw

from easy_pil import Editor, Font
from easy_pil.canvas import Canvas
from easy_pil.gradient import LinearGradient

OUT = Path(__file__).parent / "outputs"
OUT.mkdir(exist_ok=True)

# ----------------------------------------------------------------------------
# Data (fixed) — a 40-point BTC/USD trend. Last value is the current price.
# ----------------------------------------------------------------------------
PRICES = [
    61200,
    61050,
    61380,
    61600,
    61420,
    61780,
    62050,
    61900,
    62240,
    62600,
    62430,
    62180,
    62520,
    62980,
    63220,
    62950,
    62640,
    62380,
    62760,
    63150,
    63460,
    63180,
    62880,
    63320,
    63700,
    64010,
    63640,
    63360,
    63780,
    64180,
    64520,
    64260,
    63940,
    64260,
    64560,
    64380,
    64120,
    64460,
    64340,
    64182.50,
]

COIN_NAME = "Bitcoin"
COIN_TICKER = "BTC / USD"
COIN_SYMBOL = "B"

price_now = PRICES[-1]
price_open = PRICES[0]
delta = price_now - price_open
pct = delta / price_open * 100
is_up = delta >= 0

# ----------------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------------
BG_TOP = "#12151c"
BG_BOTTOM = "#0a0c11"
COIN_GRAD = LinearGradient(["#f7931a", "#ffc46b"], direction="diagonal")
UP = "#2fe38b"
DOWN = "#ff5c6c"
ACCENT = UP if is_up else DOWN
PILL_BG = "#123024" if is_up else "#33161b"
GRID = "#1b1f28"
MUTED = "#7b8494"
FAINT = "#525b6b"

W, H = 1000, 560
PAD = 56

# ----------------------------------------------------------------------------
# Card base — vertical dark gradient with a hairline top highlight.
# ----------------------------------------------------------------------------
card = Editor(Canvas((W, H), color=LinearGradient([BG_TOP, BG_BOTTOM], "vertical")))


# ----------------------------------------------------------------------------
# Sparkline geometry + smoothing
# ----------------------------------------------------------------------------
CHART_X0 = PAD
CHART_X1 = W - PAD
CHART_TOP = 244
CHART_BOT = 498
CHART_H = CHART_BOT - CHART_TOP

vmin, vmax = min(PRICES), max(PRICES)
span = vmax - vmin
lo = vmin - span * 0.16
hi = vmax + span * 0.30  # extra headroom so the peak clears the change pill


def to_px(i: int, v: float) -> tuple[float, float]:
    """Map (index, value) to pixel coordinates in the chart box."""
    x = CHART_X0 + (CHART_X1 - CHART_X0) * i / (len(PRICES) - 1)
    y = CHART_BOT - (v - lo) / (hi - lo) * CHART_H
    return (x, y)


base_pts = [to_px(i, v) for i, v in enumerate(PRICES)]


def catmull_rom(pts: list[tuple[float, float]], samples: int = 20):
    """Return a densely sampled smooth curve through the given points."""
    out: list[tuple[float, float]] = [pts[0]]
    ext = [pts[0], *pts, pts[-1]]
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for s in range(1, samples + 1):
            t = s / samples
            t2, t3 = t * t, t * t * t
            x = 0.5 * (
                2 * p1[0]
                + (-p0[0] + p2[0]) * t
                + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
            )
            y = 0.5 * (
                2 * p1[1]
                + (-p0[1] + p2[1]) * t
                + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
            )
            out.append((x, y))
    return out


curve = catmull_rom(base_pts)

# ----------------------------------------------------------------------------
# Faint horizontal grid lines behind the chart (opaque, near-bg — subtle).
# ----------------------------------------------------------------------------
for f in (0.0, 0.34, 0.68, 1.0):
    gy = int(CHART_TOP + CHART_H * f) + 4
    card.line((CHART_X0, gy), (CHART_X1, gy), width=1, fill=GRID)

# ----------------------------------------------------------------------------
# Gradient area fill under the curve.
# Built on its own layer: a solid accent polygon masked by a top->bottom
# alpha fade, then composited so it blends instead of punching holes.
# ----------------------------------------------------------------------------
poly = [*curve, (curve[-1][0], CHART_BOT + 4), (curve[0][0], CHART_BOT + 4)]

shape_mask = PilImage.new("L", (W, H), 0)
ImageDraw.Draw(shape_mask).polygon(poly, fill=255)

fade = PilImage.new("L", (W, H), 0)
fade_draw = ImageDraw.Draw(fade)
top_a, bot_a = 150, 4
for yy in range(CHART_TOP - 20, CHART_BOT + 5):
    t = (yy - (CHART_TOP - 20)) / (CHART_BOT + 5 - (CHART_TOP - 20))
    fade_draw.line((0, yy, W, yy), fill=int(top_a + (bot_a - top_a) * t))

alpha = ImageChops.multiply(shape_mask, fade)
ar, ag, ab = PilImage.new("RGB", (1, 1), ACCENT).getpixel((0, 0))
area = PilImage.new("RGBA", (W, H), (ar, ag, ab, 0))
area.putalpha(alpha)
card.paste(Editor(area), (0, 0))

# ----------------------------------------------------------------------------
# Soft glow beneath the line, then the crisp smooth line on top.
# ----------------------------------------------------------------------------
glow = Editor(Canvas((W, H), color=(0, 0, 0, 0)))
for a, b in zip(curve, curve[1:], strict=False):
    glow.line(a, b, width=9, fill=ACCENT)
glow.blur("gaussian", 7)
card.paste(glow, (0, 0), opacity=0.55)

for a, b in zip(curve, curve[1:], strict=False):
    card.line(a, b, width=4, fill=ACCENT)

# Current-price marker: outer glow ring, white ring, accent core.
mx, my = base_pts[-1]
card.ellipse(
    (mx - 12, my - 12), 24, 24, fill=(0, 0, 0, 0), outline=ACCENT, stroke_width=2
)
card.ellipse((mx - 7, my - 7), 14, 14, fill="#ffffff")
card.ellipse((mx - 4, my - 4), 8, 8, fill=ACCENT)

# ----------------------------------------------------------------------------
# Header: coin badge + name/ticker (left), price + change pill (right).
# ----------------------------------------------------------------------------
ICON = 76
coin = Editor(Canvas((ICON, ICON), color=COIN_GRAD)).circle_image()
coin.text(
    (ICON // 2, ICON // 2 - 2),
    COIN_SYMBOL,
    font=Font.poppins(variant="bold", size=42),
    color="#ffffff",
    anchor="mm",
)
card.paste(coin, (PAD, PAD))

name_x = PAD + ICON + 22
card.text(
    (name_x, PAD + 8),
    COIN_NAME,
    font=Font.poppins(variant="bold", size=34),
    color="#ffffff",
)
card.text(
    (name_x, PAD + 48),
    COIN_TICKER,
    font=Font.poppins(variant="regular", size=20),
    color=MUTED,
)

# Big current price, right-aligned.
price_str = f"${price_now:,.2f}"
card.text(
    (W - PAD, PAD),
    price_str,
    font=Font.poppins(variant="bold", size=54),
    color="#ffffff",
    anchor="rt",
)

# Change pill: sized to its contents, anchored to the right under the price.
change_str = f"{'+' if is_up else '-'}{abs(pct):.2f}%   {'+' if is_up else '-'}${abs(delta):,.0f}"
pill_font = Font.poppins(variant="bold", size=21)
text_w = int(pill_font.getlength(change_str))
pill_h = 42
tri_w = 22
pill_w = tri_w + text_w + 44
pill_x = W - PAD - pill_w
pill_y = PAD + 74

card.rectangle((pill_x, pill_y), pill_w, pill_h, fill=PILL_BG, radius=pill_h // 2)
tri_cx = pill_x + 26
tri_cy = pill_y + pill_h // 2
if is_up:
    card.regular_polygon((tri_cx, tri_cy - 1), 3, 8, rotation=0, fill=ACCENT)
else:
    card.regular_polygon((tri_cx, tri_cy + 1), 3, 8, rotation=180, fill=ACCENT)
card.text(
    (tri_cx + 16, tri_cy),
    change_str,
    font=pill_font,
    color=ACCENT,
    anchor="lm",
)

# ----------------------------------------------------------------------------
# Footer meta: range label (left) + session high / low (right).
# ----------------------------------------------------------------------------
foot_y = H - 30
card.text(
    (PAD, foot_y),
    "LAST 7 DAYS",
    font=Font.poppins(variant="bold", size=15),
    color=FAINT,
    anchor="lm",
)
card.text(
    (W - PAD, foot_y),
    f"H  ${vmax:,.0f}      L  ${vmin:,.0f}",
    font=Font.poppins(variant="regular", size=16),
    color=MUTED,
    anchor="rm",
)

card.rounded_corners(radius=28)
card.save(OUT / "crypto_ticker.png")
print("saved", OUT / "crypto_ticker.png", card.image.size)
