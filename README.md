# Easy PIL

[![PyPI](https://img.shields.io/pypi/v/easy-pil)](https://pypi.org/project/easy-pil/)
[![Lint & Test](https://github.com/shahriyardx/easy-pil/actions/workflows/lint-test.yml/badge.svg)](https://github.com/shahriyardx/easy-pil/actions/workflows/lint-test.yml)
[![License](https://img.shields.io/github/license/shahriyardx/easy-pil)](https://github.com/shahriyardx/easy-pil/blob/master/LICENSE)

A Python library built on top of [Pillow](https://github.com/python-pillow/Pillow) to easily edit/modify images.

## Installation

```bash
pip install easy-pil
```

Requires Python 3.11 or higher.

## Quick Example

```python
from easy_pil import Editor, Canvas

canvas = Canvas(width=500, height=500)
editor = Editor(canvas)

editor.text((10, 10), "Hello World")
editor.show()  # or .save("output.png")
```

## Effects System

Apply 38+ effects using the unified `effect()` method with `Effect` classes:

```python
from easy_pil import Editor, load_image
from easy_pil import Vignette, Glow, Gradient, Blur, Sepia, PixelSort

editor = Editor(load_image("image.jpg"))

# Single effect
editor.effect(Vignette(radius=120, feather=60))

# Chain multiple effects
editor.effect(Blur(amount=2)).effect(Sepia()).save("out.png")
```

### All Effects

| Category | Effects |
|----------|---------|
| **Blur & Filters** | `Blur` (box/gaussian), `Contour`, `Emboss`, `EdgeEnhance`, `Sharpen`, `Smooth`, `Pixelate` |
| **Color** | `Grayscale`, `Sepia`, `Invert`, `Posterize`, `Solarize`, `Threshold`, `Duotone` |
| **Overlay** | `ColorOverlay`, `Gradient`, `Vignette`, `Noise`, `Scanlines`, `Halftone`, `Dither` |
| **Lighting** | `Glow`, `Bloom`, `Neon`, `EdgeGlow` |
| **Shadow** | `DropShadow` |
| **Distort** | `Ripple`, `Vortex`, `Glitch`, `PixelSort`, `Kaleidoscope` |
| **Artistic** | `OilPaint`, `TiltShift`, `Sketch`, `Cartoon`, `Thermal` |
| **Region** | `PixelateRegion` |

Each `Effect` class has configurable parameters — see the [API Reference](https://easy-pil.readthedocs.io/en/latest/easy_pil/modules.html) for details.

## Text Features

```python
from easy_pil import Editor, Font, Text

editor = Editor("image.jpg")

# Simple text
editor.text((10, 10), "Hello", font=Font.poppins(size=32), color="white")

# Rich text with mixed colors/fonts
editor.rich_text((10, 50), [
    Text("Hello", Font.poppins(size=32), "red"),
    Text("World", Font.poppins(size=24), "blue"),
])

# Auto-wrapping text box
editor.text_box((10, 100), "Long text that wraps automatically...",
                font=Font.poppins(size=20), max_width=400)

# Text with drop shadow
editor.text_shadow((200, 300), "Hello", font=Font.poppins(size=40),
                   shadow_color="black", shadow_offset=(3, 3))

# Auto-fit text to width
font = editor.fit_text("Title", max_width=300, font_path="font.ttf")
editor.text((10, 10), "Title", font=font)

# Centered text
editor.centered_text((300, 400), "Centered", font=Font.poppins(size=30), align="center")
```

## Drawing Shapes

```python
editor.rectangle((10, 10), width=100, height=50, fill="red")
editor.ellipse((150, 10), width=80, height=80, outline="blue", outline_width=3)
editor.bar((10, 70), width=200, height=20, color="green")
editor.rounded_bar((10, 100), width=200, height=20, color="purple", radius=10)
editor.polygon([(300, 10), (350, 50), (250, 50)], fill="orange")
editor.arc((10, 150), width=100, height=100, start=0, end=180, fill="pink", width=3)
editor.line((10, 300), (200, 350), width=4, color="black")
editor.donut((300, 300), inner_radius=30, outer_radius=60, fill="teal")
```

## Image Adjustments

```python
editor.resize((400, 400))
editor.rotate(45, expand=True)
editor.crop((50, 50, 200, 200))
editor.flip(horizontal=True)
editor.thumbnail((200, 200))
editor.contrast(1.5)
editor.brightness(1.2)
editor.saturation(0.8)
editor.invert()
editor.blur(mode="gaussian", amount=5)
```

## Compositing

```python
editor.blend(other_image, alpha=0.5)
editor.paste(overlay, position=(50, 50))
editor.mask(mask_image, invert=False)
editor.compose([img1, img2, img3], direction="vertical", align="center")
editor.rounded_corners(radius=20)
editor.circle_image()
editor.add_border(thickness=5, color="black")
```

## Image I/O

```python
editor = Editor.open("image.png")
editor.save("output.png")
editor.show()
editor.to_bytes(fmt="PNG")  # -> bytes
```

## Async Support

```python
from easy_pil import load_image_async

img = await load_image_async("https://example.com/image.png")
```

## GIF Editing

```python
from easy_pil import GifEditor

gif = GifEditor("animation.gif")
for frame in gif.frames:
    frame.rotate(90)
gif.save("rotated.gif")
```

## Documentation

- [Introduction](https://easy-pil.readthedocs.io/en/latest/pages/intro.html)
- [Discord Bot Integration](https://easy-pil.readthedocs.io/en/latest/pages/discordbot.html)
- [Examples](https://github.com/shahriyardx/easy-pil/tree/master/examples)
- [API Reference](https://easy-pil.readthedocs.io/en/latest/easy_pil/modules.html)

## Support

- [Discord Server](https://discord.gg/fVzt5THTNb)
- [YouTube Tutorials](https://www.youtube.com/playlist?list=PLb_oBhGqAlbT4yVqV0TSXggA8b0lZhGhn)
- [Report a Bug](https://github.com/shahriyardx/easy-pil/issues/)
