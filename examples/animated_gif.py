"""Animated GIF processing with GifEditor.

Builds a looping animation of three orbiting, glowing orbs entirely in memory,
then loads it with ``GifEditor`` and applies an effect to EVERY frame with a
single call. ``GifEditor`` queues the operation and replays it against one
decoded frame at a time, so memory stays bounded no matter how many frames.
Fully self-contained — no external assets.
"""

import math
from io import BytesIO
from pathlib import Path

from easy_pil import Bloom, Editor, GifEditor, Glow
from easy_pil.canvas import Canvas
from easy_pil.gradient import LinearGradient

OUT = Path(__file__).parent / "outputs"
OUT.mkdir(exist_ok=True)

SIZE = 512
FRAMES = 24
RADIUS = 130
CX = CY = SIZE // 2
ORBS = ["#ff6ec4", "#43e97b", "#38bdf8"]
DURATION = 60  # ms per frame


def build_source() -> BytesIO:
    """Render the orbiting-orbs animation to an in-memory GIF."""
    frames = []
    for i in range(FRAMES):
        frame = Editor(
            Canvas(
                (SIZE, SIZE),
                color=LinearGradient(["#0f2027", "#203a43", "#2c5364"], "vertical"),
            )
        )
        for k, color in enumerate(ORBS):
            ang = 2 * math.pi * (i / FRAMES) + k * 2 * math.pi / 3
            x = CX + RADIUS * math.cos(ang)
            y = CY + RADIUS * math.sin(ang)
            orb = Editor(Canvas((168, 168), color=(0, 0, 0, 0)))
            orb.ellipse((24, 24), 120, 120, fill=color)
            orb.effect(Glow(radius=32, color=color, alpha=0.85))
            frame.paste(orb, (int(x - 84), int(y - 84)))
        frames.append(frame.image.convert("RGB"))

    buf = BytesIO()
    frames[0].save(
        buf,
        "GIF",
        save_all=True,
        append_images=frames[1:],
        duration=DURATION,
        loop=0,
    )
    buf.seek(0)
    return buf


# 1) Make the source animation.
source = build_source()

# 2) Load it and stylise EVERY frame. Both calls are QUEUED and replayed
#    against one decoded frame at a time — only a single frame is in memory,
#    no matter the frame count.
gif = GifEditor(source)
gif.saturation(1.3)
gif.effect(Bloom(threshold=150, radius=30, intensity=0.55))
gif.save(OUT / "animated_gif.gif")

# 3) Also drop a PNG of the first processed frame so the result is easy to
#    preview in docs (GIFs animate on GitHub; static viewers show a still).
from PIL import Image  # noqa: E402  (local import, only for the preview still)

Image.open(OUT / "animated_gif.gif").convert("RGBA").save(
    OUT / "animated_gif_preview.png"
)

print("saved", OUT / "animated_gif.gif", f"({FRAMES} frames)")
