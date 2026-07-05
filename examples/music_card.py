"""Now-playing music card.

Showcases: an ambient blurred backdrop derived from the album art, a squircle
album cover with a soft drop shadow, a gradient progress bar, and a clean type
hierarchy. Fully self-contained — no external assets.
"""

from pathlib import Path

from easy_pil import ColorOverlay, DropShadow, Editor, Font
from easy_pil.canvas import Canvas
from easy_pil.gradient import LinearGradient

OUT = Path(__file__).parent / "outputs"
OUT.mkdir(exist_ok=True)

W, H = 1000, 420
ACCENT = "#ffb457"
ALBUM = LinearGradient(["#f5567b", "#ffb457"], direction="diagonal")

# Ambient backdrop: an enlarged, blurred wash of the album colours, dimmed so
# the foreground text stays crisp.
ambient = Editor(Canvas((W, H), color=ALBUM)).blur("gaussian", 70)
card = Editor(Canvas((W, H), color="#0d0d12"))
card.paste(ambient, (0, 0), opacity=0.5)
card.effect(ColorOverlay((8, 8, 12), alpha=0.52))

# Album cover: a squircle inset in a padded canvas so its shadow has room.
art = Editor(Canvas((380, 380), color=(0, 0, 0, 0)))
art.squircle((40, 40), 300, 300, radius_ratio=0.36, fill=ALBUM)
art.effect(DropShadow(offset=(0, 18), blur_radius=34, color=(0, 0, 0), alpha=0.55))
card.paste(art, (20, 20))

TX = 410

# Eyebrow label (letter-spaced by hand) in the accent colour.
card.text(
    (TX, 70),
    "N O W   P L A Y I N G",
    font=Font.poppins(variant="bold", size=17),
    color=ACCENT,
)
# Title + artist.
card.text(
    (TX, 104),
    "Golden Hour",
    font=Font.poppins(variant="bold", size=58),
    color="#ffffff",
)
card.text(
    (TX, 182),
    "JVKE",
    font=Font.poppins(variant="light", size=28),
    color="#b7b7c4",
)

# Progress: a slim gradient track with a knob and timestamps.
BAR_Y = 300
BAR_W = 440
pct = 42
card.rounded_bar(
    (TX, BAR_Y),
    BAR_W,
    8,
    percentage=100,
    fill="#2a2a33",
)
card.rounded_bar(
    (TX, BAR_Y),
    BAR_W,
    8,
    percentage=pct,
    fill=LinearGradient(["#f5567b", "#ffb457"]),
)
knob_x = TX + int(BAR_W * pct / 100)
card.ellipse((knob_x - 8, BAR_Y - 4), 16, 16, fill="#ffffff")
card.text(
    (TX, 322),
    "1:47",
    font=Font.poppins(variant="regular", size=18),
    color="#8b8b98",
)
card.text(
    (TX + BAR_W, 322),
    "4:12",
    font=Font.poppins(variant="regular", size=18),
    color="#8b8b98",
    align="right",
)

# Play button: accent circle with a triangle glyph.
btn_cx, btn_cy = TX + BAR_W + 55, BAR_Y + 4
card.ellipse((btn_cx - 34, btn_cy - 34), 68, 68, fill=ACCENT)
# Right-pointing triangle (rotate a 3-gon), nudged for optical centering.
card.regular_polygon((btn_cx + 3, btn_cy), 3, 17, rotation=90, fill="#0d0d12")

card.save(OUT / "music_card.png")
print("saved", OUT / "music_card.png", card.image.size)
