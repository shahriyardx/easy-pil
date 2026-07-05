"""Product-analytics stats dashboard.

Showcases: gradient header, a row of KPI stat tiles with signed deltas,
a donut ring gauge built from a faint track ring plus a coloured
percentage arc, and a categorical vertical bar chart with a muted
value grid and axis labels. Dark data-viz aesthetic, one coherent
cyan-blue accent family. Fully self-contained — no external assets.
"""

from pathlib import Path

from easy_pil import Editor, Font
from easy_pil.canvas import Canvas
from easy_pil.gradient import LinearGradient

OUT = Path(__file__).parent / "outputs"
OUT.mkdir(exist_ok=True)

# --- Palette -------------------------------------------------------------
W, H = 1040, 720
BG_TOP, BG_BOT = "#0e0f1a", "#0a0a12"
PANEL = "#15161f"
PANEL_LINE = "#242636"
TEXT = "#eef0f7"
MUTED = "#8b90a6"
FAINT = "#565b73"
GRID = "#22243250"
ACCENT = LinearGradient(["#22d3ee", "#3b82f6"], direction="vertical")
ACCENT_SOLID = "#38bdf8"
POS = "#34d399"  # green — positive delta
NEG = "#fb7185"  # rose  — negative delta
TRACK = "#232536"

# Fonts.
F_TITLE = Font.poppins(variant="bold", size=38)
F_SUB = Font.poppins(variant="light", size=18)
F_KPI = Font.poppins(variant="bold", size=34)
F_LABEL = Font.poppins(variant="regular", size=15)
F_DELTA = Font.poppins(variant="regular", size=15)
F_SECTION = Font.poppins(variant="bold", size=20)
F_AXIS = Font.poppins(variant="regular", size=13)
F_GAUGE = Font.poppins(variant="bold", size=52)
F_GAUGE_SM = Font.poppins(variant="regular", size=16)

PAD = 40

card = Editor(
    Canvas((W, H), color=LinearGradient([BG_TOP, BG_BOT], direction="vertical"))
)


def panel(x, y, w, h, radius=18):
    """Draw a solid rounded panel with a hairline border."""
    card.rectangle((x, y), w, h, fill=PANEL, radius=radius)
    card.rectangle(
        (x, y), w, h, fill=None, outline=PANEL_LINE, stroke_width=1, radius=radius
    )


def tri_up(cx, cy, s, fill):
    """Small upward triangle marker centred at (cx, cy)."""
    card.polygon([(cx - s, cy + s), (cx + s, cy + s), (cx, cy - s)], fill=fill)


def tri_down(cx, cy, s, fill):
    """Small downward triangle marker centred at (cx, cy)."""
    card.polygon([(cx - s, cy - s), (cx + s, cy - s), (cx, cy + s)], fill=fill)


# --- Header --------------------------------------------------------------
card.gradient_text(
    (PAD, 42),
    "Analytics Overview",
    F_TITLE,
    LinearGradient(["#e7ecff", "#9fb4ff"]),
    anchor="lt",
)
card.text(
    (PAD + 2, 92),
    "Performance summary  •  Jun 1 – Jun 30, 2026",
    font=F_SUB,
    color=MUTED,
    anchor="lt",
)

# "Last 30 days" pill, top-right.
pill_w, pill_h = 148, 34
pill_x, pill_y = W - PAD - pill_w, 52
card.rectangle((pill_x, pill_y), pill_w, pill_h, fill="#191b28", radius=17)
card.rectangle(
    (pill_x, pill_y),
    pill_w,
    pill_h,
    fill=None,
    outline=PANEL_LINE,
    stroke_width=1,
    radius=17,
)
card.ellipse((pill_x + 18, pill_y + pill_h // 2 - 4), 8, 8, fill=ACCENT_SOLID)
card.text(
    (pill_x + 40, pill_y + pill_h // 2),
    "Last 30 days",
    font=F_LABEL,
    color=TEXT,
    anchor="lm",
)

# --- KPI stat tiles ------------------------------------------------------
KPIS = [
    ("REVENUE", "$84.2k", "+12.5%", True),
    ("ACTIVE USERS", "18,420", "+8.2%", True),
    ("CONVERSION", "3.7%", "-1.4%", False),
    ("AVG. SESSION", "4m 12s", "+3.1%", True),
]

tiles_y = 150
tile_h = 132
gap = 20
usable = W - 2 * PAD
tile_w = (usable - gap * (len(KPIS) - 1)) / len(KPIS)

for i, (label, value, delta, positive) in enumerate(KPIS):
    x = PAD + i * (tile_w + gap)
    panel(x, tiles_y, tile_w, tile_h)
    # Label (top).
    card.text((x + 22, tiles_y + 24), label, font=F_LABEL, color=MUTED, anchor="lt")
    # Big number.
    card.text((x + 22, tiles_y + 58), value, font=F_KPI, color=TEXT, anchor="lt")
    # Delta with triangle marker (bottom).
    dcol = POS if positive else NEG
    dy = tiles_y + tile_h - 26
    if positive:
        tri_up(x + 27, dy, 5, dcol)
    else:
        tri_down(x + 27, dy, 5, dcol)
    card.text((x + 40, dy), delta, font=F_DELTA, color=dcol, anchor="lm")
    card.text((x + 40 + 62, dy), "vs last mo.", font=F_AXIS, color=FAINT, anchor="lm")

# --- Lower section: bar chart (left) + donut gauge (right) ---------------
low_y = tiles_y + tile_h + gap
low_h = H - low_y - PAD

bar_w = 600
donut_w = usable - bar_w - gap
bar_x = PAD
donut_x = PAD + bar_w + gap

# ---- Bar chart panel ----
panel(bar_x, low_y, bar_w, low_h)
card.text(
    (bar_x + 24, low_y + 22), "Weekly Revenue", font=F_SECTION, color=TEXT, anchor="lt"
)
card.text(
    (bar_x + 24, low_y + 52),
    "Revenue by day  ($000s)",
    font=F_AXIS,
    color=MUTED,
    anchor="lt",
)

BARS = [
    ("Mon", 42),
    ("Tue", 58),
    ("Wed", 51),
    ("Thu", 69),
    ("Fri", 84),
    ("Sat", 76),
    ("Sun", 63),
]
axis_max = 100

# Plot geometry inside the panel.
plot_left = bar_x + 66
plot_right = bar_x + bar_w - 28
plot_top = low_y + 92
plot_bottom = low_y + low_h - 46
plot_h = plot_bottom - plot_top

# Horizontal grid lines + y-axis value labels.
for gv in range(0, axis_max + 1, 25):
    gy = plot_bottom - (gv / axis_max) * plot_h
    card.line((plot_left, gy), (plot_right, gy), width=1, fill=GRID)
    card.text((plot_left - 14, gy), str(gv), font=F_AXIS, color=FAINT, anchor="rm")

# Baseline (slightly stronger).
card.line((plot_left, plot_bottom), (plot_right, plot_bottom), width=2, fill=PANEL_LINE)

# Bars.
slot = (plot_right - plot_left) / len(BARS)
bw = 34
peak = max(v for _, v in BARS)
for i, (day, val) in enumerate(BARS):
    cx = plot_left + slot * (i + 0.5)
    bh = (val / axis_max) * plot_h
    bx = cx - bw / 2
    by = plot_bottom - bh
    fill = (
        ACCENT
        if val == peak
        else LinearGradient(["#2a4d6e", "#213a58"], direction="vertical")
    )
    card.rectangle((bx, by), bw, bh, fill=fill, radius=7)
    # Category label.
    card.text((cx, plot_bottom + 20), day, font=F_AXIS, color=MUTED, anchor="mm")
    # Value label above the peak bar for emphasis.
    if val == peak:
        card.text((cx, by - 14), str(val), font=F_AXIS, color=ACCENT_SOLID, anchor="mm")

# ---- Donut gauge panel ----
panel(donut_x, low_y, donut_w, low_h)
card.text(
    (donut_x + 24, low_y + 22),
    "Goal Completion",
    font=F_SECTION,
    color=TEXT,
    anchor="lt",
)
card.text(
    (donut_x + 24, low_y + 52),
    "Monthly target",
    font=F_AXIS,
    color=MUTED,
    anchor="lt",
)

pct = 73
gcx = donut_x + donut_w / 2
gcy = low_y + low_h / 2 + 24
ring_out = 108
ring_in = 84
ring_thick = ring_out - ring_in

# Faint full track ring.
card.donut((gcx, gcy), ring_in, ring_out, fill=TRACK)

# Coloured percentage arc on top (0deg at top, clockwise).
arc_r = ring_out - ring_thick / 2
card.arc(
    (gcx - arc_r, gcy - arc_r),
    arc_r * 2,
    arc_r * 2,
    0,
    360 * pct / 100,
    fill=LinearGradient(["#22d3ee", "#3b82f6"], direction="diagonal"),
    stroke_width=ring_thick,
)

# Centre labels.
card.text((gcx, gcy - 8), f"{pct}%", font=F_GAUGE, color=TEXT, anchor="mm")
card.text((gcx, gcy + 34), "of $115k goal", font=F_GAUGE_SM, color=MUTED, anchor="mm")

# Legend row beneath the ring.
leg_y = low_y + low_h - 34
card.ellipse((gcx - 92, leg_y - 5), 10, 10, fill=ACCENT_SOLID)
card.text((gcx - 76, leg_y), "Reached", font=F_AXIS, color=MUTED, anchor="lm")
card.ellipse((gcx + 18, leg_y - 5), 10, 10, fill="#3a3d52")
card.text((gcx + 34, leg_y), "Remaining", font=F_AXIS, color=MUTED, anchor="lm")

card.save(OUT / "stats_dashboard.png")
print("saved", OUT / "stats_dashboard.png")
