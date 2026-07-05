"""Top-players leaderboard.

Showcases: gradient_text header, per-row panels via rounded rectangles,
medal rank badges, circular avatars, per-row score bars, and a tidy type
hierarchy. Fully self-contained — no external assets.
"""

from pathlib import Path

from easy_pil import Editor, Font
from easy_pil.canvas import Canvas
from easy_pil.gradient import LinearGradient, RadialGradient

OUT = Path(__file__).parent / "outputs"
OUT.mkdir(exist_ok=True)

W, H = 900, 500
MUTED = "#8b90a6"

card = Editor(
    Canvas((W, H), color=LinearGradient(["#141428", "#0b0b14"], direction="vertical"))
)

# Header.
card.gradient_text(
    (50, 46),
    "TOP PLAYERS",
    Font.poppins(variant="bold", size=40),
    LinearGradient(["#7f5af0", "#2cb1ff"]),
)
card.text(
    (52, 96),
    "Season 12  •  Global",
    font=Font.poppins(variant="light", size=20),
    color=MUTED,
)

MEDALS = [
    LinearGradient(["#f7971e", "#ffd200"]),  # gold
    LinearGradient(["#bdc3c7", "#e7eaec"]),  # silver
    LinearGradient(["#b06f42", "#e0a56e"]),  # bronze
]
AVATARS = [
    ["#f6d365", "#fda085"],
    ["#a1c4fd", "#c2e9fb"],
    ["#fbc2eb", "#a6c1ee"],
]
ROWS = [
    ("Nova Sterling", "Level 47", 9820, 100),
    ("Kai Rivera", "Level 44", 8710, 89),
    ("Mira Chen", "Level 41", 7640, 78),
]

row_y = 150
ROW_H = 96
for i, (name, sub, score, pct) in enumerate(ROWS):
    y = row_y + i * (ROW_H + 16)
    # Row panel — built on its own layer then composited, so the translucent
    # fill blends over the background instead of overwriting it.
    panel = Editor(Canvas((W - 100, ROW_H), color=(0, 0, 0, 0)))
    panel.rectangle((0, 0), W - 100, ROW_H, fill=(255, 255, 255, 16), radius=20)
    card.paste(panel, (50, y))

    # Rank medal.
    cy = y + ROW_H // 2
    card.donut((104, cy), 22, 30, fill=MEDALS[i])
    card.text(
        (104, cy),
        str(i + 1),
        font=Font.poppins(variant="bold", size=26),
        color="#ffffff",
        anchor="mm",
    )

    # Avatar.
    av = Editor(Canvas((64, 64), color=RadialGradient(AVATARS[i])))
    av.circle_image()
    card.paste(av, (160, cy - 32))

    # Name + sub.
    card.text(
        (244, cy - 20),
        name,
        font=Font.poppins(variant="bold", size=26),
        color="#ffffff",
    )
    card.text(
        (246, cy + 14),
        sub,
        font=Font.poppins(variant="regular", size=16),
        color=MUTED,
    )

    # Score bar + value on the right.
    card.rounded_bar((540, cy - 4), 180, 8, percentage=100, fill="#23232e")
    card.rounded_bar(
        (540, cy - 4),
        180,
        8,
        percentage=pct,
        fill=LinearGradient(["#7f5af0", "#2cb1ff"]),
    )
    card.text(
        (W - 60, cy),
        f"{score:,}",
        font=Font.poppins(variant="bold", size=24),
        color="#e6ebf2",
        anchor="rm",
    )

card.save(OUT / "leaderboard.png")
print("saved", OUT / "leaderboard.png", card.image.size)
