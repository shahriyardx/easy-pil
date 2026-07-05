"""Server welcome banner.

Showcases: an ambient radial wash, a centred avatar in a gradient ring,
gradient_text, scattered star confetti, and centred type. Fully
self-contained — no external assets.
"""

from pathlib import Path

from easy_pil import ColorOverlay, Editor, Font
from easy_pil.canvas import Canvas
from easy_pil.gradient import LinearGradient, RadialGradient

OUT = Path(__file__).parent / "outputs"
OUT.mkdir(exist_ok=True)

W, H = 1000, 400
ACCENT = LinearGradient(["#38f9d7", "#43e97b"])
MUTED = "#93a0b4"

# Ambient glow blooming from the top-centre.
ambient = Editor(
    Canvas((W, H), color=RadialGradient(["#0f9b8e", "#0b0e14"], center=(0.5, 0.0)))
).blur("gaussian", 80)
card = Editor(Canvas((W, H), color="#0b0e14"))
card.paste(ambient, (0, 0), opacity=0.6)
card.effect(ColorOverlay((9, 12, 18), alpha=0.34))

# Star confetti scattered across the top.
confetti = [
    (120, 60, 10),
    (250, 110, 6),
    (820, 70, 11),
    (910, 140, 7),
    (700, 50, 6),
    (170, 150, 7),
    (500, 40, 8),
    (350, 70, 6),
]
for cx, cy, r in confetti:
    card.star((cx, cy), 5, r, r * 0.45, fill=(120, 230, 200, 120))

# Avatar: gradient ring with circular avatar seated inside.
AV_CX, AV_CY = W // 2, 140
card.donut((AV_CX, AV_CY), 78, 86, fill=ACCENT)
avatar = Editor(Canvas((150, 150), color=RadialGradient(["#f6d365", "#fda085"])))
avatar.circle_image()
card.paste(avatar, (AV_CX - 75, AV_CY - 75))

# Headline + details, all centred.
card.gradient_text(
    (W // 2, 260),
    "WELCOME",
    Font.poppins(variant="bold", size=64),
    ACCENT,
    anchor="mm",
)
card.text(
    (W // 2, 312),
    "Nova Sterling just joined the server",
    font=Font.poppins(variant="regular", size=24),
    color="#e6ebf2",
    anchor="mm",
)
card.text(
    (W // 2, 348),
    "You are our 1,024th member",
    font=Font.poppins(variant="light", size=19),
    color=MUTED,
    anchor="mm",
)

card.save(OUT / "welcome_banner.png")
print("saved", OUT / "welcome_banner.png", card.image.size)
