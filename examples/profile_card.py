"""Profile / rank card.

Showcases: an ambient radial wash, a circular avatar inside a gradient donut
ring, a gradient level pill, a stat row, and a slim gradient XP bar with a
knob. Fully self-contained — no external assets.
"""

from pathlib import Path

from easy_pil import ColorOverlay, Editor, Font
from easy_pil.canvas import Canvas
from easy_pil.gradient import LinearGradient, RadialGradient

OUT = Path(__file__).parent / "outputs"
OUT.mkdir(exist_ok=True)

W, H = 1000, 340
ACCENT = LinearGradient(["#7f5af0", "#2cb1ff"])
MUTED = "#8b90a6"

# Ambient wash bleeding in from the top-right, dimmed for contrast.
ambient = Editor(
    Canvas((W, H), color=RadialGradient(["#7f5af0", "#0e0e14"], center=(0.85, 0.15)))
).blur("gaussian", 80)
card = Editor(Canvas((W, H), color="#0e0e14"))
card.paste(ambient, (0, 0), opacity=0.6)
card.effect(ColorOverlay((10, 10, 18), alpha=0.38))

# Avatar: gradient donut ring with a circular avatar seated inside it.
AV_CX, AV_CY = 140, 170
card.donut((AV_CX, AV_CY), 96, 105, fill=ACCENT)
avatar = Editor(Canvas((184, 184), color=RadialGradient(["#f6d365", "#fda085"])))
avatar.circle_image()
card.paste(avatar, (AV_CX - 92, AV_CY - 92))

TX = 285

# Name + handle.
card.text(
    (TX, 66),
    "Nova Sterling",
    font=Font.poppins(variant="bold", size=46),
    color="#ffffff",
)
card.text(
    (TX, 128),
    "@novasterling",
    font=Font.poppins(variant="light", size=24),
    color=MUTED,
)

# Level pill.
PILL_Y = 178
card.rectangle((TX, PILL_Y), 138, 40, fill=ACCENT, radius=20)
card.text(
    (TX + 69, PILL_Y + 20),
    "LEVEL 47",
    font=Font.poppins(variant="bold", size=17),
    color="#ffffff",
    anchor="mm",
)

# Stat row on the right.
stats = [("RANK", "#4"), ("GAMES", "312"), ("WIN RATE", "68%")]
for i, (label, value) in enumerate(stats):
    sx = 560 + i * 150
    card.text(
        (sx, PILL_Y - 6),
        value,
        font=Font.poppins(variant="bold", size=34),
        color="#ffffff",
    )
    card.text(
        (sx, PILL_Y + 34),
        label,
        font=Font.poppins(variant="regular", size=14),
        color=MUTED,
    )

# Slim XP bar with a knob.
BAR_X, BAR_Y, BAR_W = TX, 268, W - TX - 50
pct = 74
card.rounded_bar((BAR_X, BAR_Y), BAR_W, 10, percentage=100, fill="#23232e")
card.rounded_bar((BAR_X, BAR_Y), BAR_W, 10, percentage=pct, fill=ACCENT)
knob_x = BAR_X + int(BAR_W * pct / 100)
card.ellipse((knob_x - 9, BAR_Y - 4), 18, 18, fill="#ffffff")
card.text(
    (BAR_X, BAR_Y + 22),
    "7,400 / 10,000 XP",
    font=Font.poppins(variant="regular", size=16),
    color=MUTED,
)

card.save(OUT / "profile_card.png")
print("saved", OUT / "profile_card.png", card.image.size)
