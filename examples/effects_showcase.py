"""Effects showcase grid.

Renders one procedural "landscape" source, applies a range of effects to
copies of it, and lays them out as a labelled, rounded-tile grid. Showcases:
Editor.copy, the effect pipeline, rounded_corners, and Editor.compose.
Fully self-contained — no external assets.
"""

from pathlib import Path

from easy_pil import (
    Bloom,
    Cartoon,
    Duotone,
    Editor,
    Font,
    Halftone,
    Sepia,
)
from easy_pil.canvas import Canvas
from easy_pil.gradient import LinearGradient

OUT = Path(__file__).parent / "outputs"
OUT.mkdir(exist_ok=True)

S = 260
LABEL_H = 46
FONT = Font.poppins(variant="bold", size=20)


def make_source() -> Editor:
    """A small procedural sunset landscape to feed the effects."""
    src = Editor(
        Canvas(
            (S, S), color=LinearGradient(["#2b3a67", "#ff9a56"], direction="vertical")
        )
    )
    src.ellipse((int(S * 0.58), int(S * 0.18)), 62, 62, fill="#ffe29a")
    src.triangle((-20, int(S * 0.52)), 150, int(S * 0.5), fill="#20344f")
    src.triangle((int(S * 0.38), int(S * 0.44)), 190, int(S * 0.6), fill="#15253a")
    return src


def tile(source: Editor, label: str, effect=None) -> Editor:
    """Build a labelled, rounded tile for one effect variant."""
    img = source.copy()
    if effect is not None:
        img.effect(effect)
    frame = Editor(Canvas((S, S + LABEL_H), color="#12121c"))
    frame.paste(img, (0, 0))
    frame.text(
        (S // 2, S + LABEL_H // 2),
        label,
        font=FONT,
        color="#e6ebf2",
        anchor="mm",
    )
    frame.rounded_corners(radius=20, offset=0)
    return frame


source = make_source()
variants = [
    tile(source, "Original"),
    tile(source, "Duotone", Duotone((22, 20, 74), (255, 180, 120))),
    tile(source, "Sepia", Sepia()),
    tile(source, "Bloom", Bloom(threshold=170, radius=12, intensity=0.55)),
    tile(source, "Halftone", Halftone(dot_size=6)),
    tile(source, "Cartoon", Cartoon(colors=4, edge_thickness=1)),
]

# 3 columns x 2 rows.
rows = []
for r in range(0, len(variants), 3):
    row = Editor(Canvas((10, 10))).compose(
        variants[r : r + 3], direction="horizontal", spacing=22
    )
    rows.append(row)
grid = Editor(Canvas((10, 10))).compose(rows, direction="vertical", spacing=22)

PAD = 46
canvas = Editor(
    Canvas(
        (grid.image.width + PAD * 2, grid.image.height + PAD * 2 + 56),
        color=LinearGradient(["#0f1020", "#161a2e"], direction="vertical"),
    )
)
canvas.gradient_text(
    (canvas.image.width // 2, 46),
    "EASY-PIL EFFECTS",
    Font.poppins(variant="bold", size=38),
    LinearGradient(["#7f5af0", "#2cb1ff"]),
    anchor="mm",
)
canvas.paste(grid, (PAD, 84))

canvas.save(OUT / "effects_showcase.png")
print("saved", OUT / "effects_showcase.png", canvas.image.size)
