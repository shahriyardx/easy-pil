"""Editorial pull-quote card for social media.

Showcases: a rich diagonal plum-to-rose gradient lifted by a warm radial
glow and a gentle vignette, an oversized typographic quotation mark, a
centered wrapped pull-quote, hairline gold rules, and an author row with a
procedural gradient avatar wrapped in a gold ring. Fully self-contained —
no external assets, no network.
"""

from pathlib import Path

from easy_pil import Editor, Font, Noise, Vignette
from easy_pil.canvas import Canvas
from easy_pil.gradient import LinearGradient, RadialGradient

OUT = Path(__file__).parent / "outputs"
OUT.mkdir(exist_ok=True)

W, H = 1080, 1350
CX = W // 2

# Palette: deep plum -> rose base, warm gold accent, cream text.
GOLD = "#e6c88f"
GOLD_RGBA = (230, 200, 143)
CREAM = "#f6efe4"

QUOTE = (
    "The people who are crazy enough to think they can change the "
    "world are the ones who do."
)
NAME = "Isabella Moreau"
HANDLE = "@isabella.writes"


# --- Background: layered gradient, warm glow and a gentle vignette --------
card = Editor(
    Canvas(
        (W, H),
        color=LinearGradient(
            ["#3d1c58", "#7a3060", "#c0546c"],
            direction="diagonal",
        ),
    )
)

# A soft warm glow behind the quote to draw the eye toward the centre.
glow_layer = Editor(
    Canvas(
        (W, H),
        color=RadialGradient(["#d76b81", "#3d1c58"], center=(0.5, 0.36)),
    )
)
card.paste(glow_layer, (0, 0), opacity=0.55)

# Gentle vignette: only softens the far corners, keeps the gradient rich.
card.effect(Vignette(radius=800, color=(28, 12, 40), feather=300))

# --- Inset hairline frame (built on its own layer so it blends) ----------
M = 56
frame = Editor(Canvas((W, H), color=(0, 0, 0, 0)))
frame.rectangle(
    (M, M),
    W - 2 * M,
    H - 2 * M,
    fill=(0, 0, 0, 0),
    radius=18,
    outline=(*GOLD_RGBA, 110),
    stroke_width=2,
)
card.paste(frame, (0, 0))

# --- Eyebrow label -------------------------------------------------------
card.text(
    (CX, 195),
    "W O R D S   T O   L I V E   B Y",
    font=Font.poppins(variant="bold", size=22),
    color=GOLD,
    anchor="mm",
)
card.line((CX - 46, 227), (CX + 46, 227), width=2, fill=(*GOLD_RGBA, 150))

# --- Oversized opening quotation mark (translucent layer) ----------------
mark = Editor(Canvas((420, 420), color=(0, 0, 0, 0)))
mark.text(
    (210, 210),
    "“",
    font=Font.montserrat(variant="bold", size=440),
    color=GOLD,
    anchor="mm",
)
card.paste(mark, (CX - 210, 240), opacity=0.85)

# --- The pull-quote (measured, then anchored) ----------------------------
QUOTE_FONT = Font.montserrat(variant="light", size=58)
QUOTE_W = 760
LINE_SPACING = 22

# Measure wrapped height on a throwaway layer to place the author row.
probe = Editor(Canvas((W, H), color=(0, 0, 0, 0)))
probe.text_box(
    (CX - QUOTE_W // 2, 0),
    QUOTE,
    font=QUOTE_FONT,
    color=CREAM,
    align="center",
    max_width=QUOTE_W,
    line_spacing=LINE_SPACING,
)
_, top, _, bottom = probe.last_text_bbox
quote_h = bottom - top

quote_top = 555
card.text_box(
    (CX - QUOTE_W // 2, quote_top),
    QUOTE,
    font=QUOTE_FONT,
    color=CREAM,
    align="center",
    max_width=QUOTE_W,
    line_spacing=LINE_SPACING,
)

# --- Divider + author row ------------------------------------------------
quote_bottom = quote_top + quote_h
author_y = quote_bottom + 150
card.line(
    (CX - 40, author_y - 78),
    (CX + 40, author_y - 78),
    width=2,
    fill=(*GOLD_RGBA, 170),
)

# Procedural circular avatar wrapped in a gold ring.
AV = 96
RING = 5
avatar = Editor(
    Canvas(
        (AV, AV),
        color=RadialGradient(["#ffd8a6", "#d0708a", "#5c2b56"], center=(0.35, 0.3)),
    )
).circle_image()

ring_d = AV + RING * 2
ring = Editor(Canvas((ring_d, ring_d), color=(0, 0, 0, 0)))
ring.ellipse((0, 0), ring_d, ring_d, fill=GOLD)
ring.paste(avatar, (RING, RING))

# Author block: avatar on the left, name + handle stacked to its right.
name_font = Font.poppins(variant="bold", size=34)
handle_font = Font.poppins(variant="regular", size=26)
name_w = name_font.getlength(NAME)
handle_w = handle_font.getlength(HANDLE)
gap = 26
group_w = ring_d + gap + max(name_w, handle_w)
group_left = int(CX - group_w // 2)

avatar_cy = author_y + 4
card.paste(ring, (group_left, avatar_cy - ring_d // 2))

text_x = group_left + ring_d + gap
card.text(
    (text_x, avatar_cy - 20),
    NAME,
    font=name_font,
    color=CREAM,
    anchor="lm",
)
card.text(
    (text_x, avatar_cy + 22),
    HANDLE,
    font=handle_font,
    color=GOLD,
    anchor="lm",
)

# --- Small centred ornament to close the composition ---------------------
dot_y = 1215
for dx, r in ((-22, 3), (0, 5), (22, 3)):
    card.ellipse((CX + dx - r, dot_y - r), r * 2, r * 2, fill=GOLD)

# --- Film grain for a premium, printed finish ----------------------------
card.effect(Noise(intensity=0.04, monochrome=True))

card.save(OUT / "quote_card.png")
print("saved", OUT / "quote_card.png", card.image.size)
