"""Effect classes for the Editor.effect() method."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod

import numpy as np
from PIL import Image as PilImage
from PIL import ImageDraw, ImageFilter, ImageOps

from ._nputil import as_rgba, build_lut, from_array, lut_from_t
from .canvas import Color
from .color import to_rgb, to_rgba


class Effect(ABC):
    """Base class for all effects. Subclass and implement apply()."""

    @abstractmethod
    def apply(self, image: PilImage.Image) -> PilImage.Image:
        """Apply effect to image, return modified copy."""


class Vignette(Effect):
    """
    Darken edges of image with radial gradient.

    Parameters
    ----------
    radius : float, optional
        Radius of protected center area, by default 100
    color : Color, optional
        Vignette color, by default (0, 0, 0)
    feather : float, optional
        Blur radius for edge softness, by default 50

    """

    def __init__(
        self,
        radius: float = 100,
        color: Color = (0, 0, 0),
        feather: float = 50,
    ) -> None:
        self.radius = radius
        self.feather = feather
        if isinstance(color, (int, str)):
            self.color = color
        else:
            self.color = tuple(color)  # type: ignore[arg-type]

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        w, h = image.size
        cx, cy = w // 2, h // 2
        rx = max(cx - int(self.radius), 1) if cx > 0 else 0
        ry = max(cy - int(self.radius), 1) if cy > 0 else 0

        mask = PilImage.new("L", (w, h), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)

        if self.feather > 0:
            mask = mask.filter(ImageFilter.GaussianBlur(radius=self.feather))

        mask = ImageOps.invert(mask)

        color_rgba = to_rgba(self.color)

        color_layer = PilImage.new("RGBA", (w, h), color_rgba)
        color_layer.putalpha(mask)

        result = as_rgba(image)
        return PilImage.alpha_composite(result, color_layer)


class ColorOverlay(Effect):
    """
    Overlay solid color with transparency over image.

    Parameters
    ----------
    color : Color
        Overlay color.
    alpha : float, optional
        Opacity 0-1, by default 0.5. Ignored if color includes alpha.

    """

    def __init__(self, color: Color, alpha: float = 0.5) -> None:
        self.alpha = alpha
        if isinstance(color, (int, str)):
            self.color = color
        else:
            self.color = tuple(color)

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        w, h = image.size

        rgba = to_rgba(self.color, alpha=int(self.alpha * 255))
        overlay = PilImage.new("RGBA", (w, h), rgba)

        result = as_rgba(image)
        return PilImage.alpha_composite(result, overlay)


class DropShadow(Effect):
    """
    Add drop shadow behind image content.

    Parameters
    ----------
    offset : tuple[int, int], optional
        Shadow offset (x, y), by default (5, 5)
    blur_radius : int, optional
        Blur radius for shadow softness, by default 10
    color : Color, optional
        Shadow color, by default (0, 0, 0)
    alpha : float, optional
        Shadow opacity 0-1, by default 0.5

    """

    def __init__(
        self,
        offset: tuple[int, int] = (5, 5),
        blur_radius: int = 10,
        color: Color = (0, 0, 0),
        alpha: float = 0.5,
    ) -> None:
        self.offset = offset
        self.blur_radius = blur_radius
        self.alpha = alpha
        if isinstance(color, (int, str)):
            self.color = color
        else:
            self.color = tuple(color)

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        w, h = image.size
        source = as_rgba(image)
        alpha_channel = source.split()[3]

        color_rgba = to_rgba(self.color, alpha=int(self.alpha * 255))

        # Solid shadow color, shaped by the source alpha scaled by opacity.
        shadow = PilImage.new("RGBA", (w, h), (*color_rgba[:3], 0))
        shadow.putalpha(alpha_channel.point(lambda x: int(x * (color_rgba[3] / 255))))

        if self.blur_radius > 0:
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=self.blur_radius))

        result = PilImage.new("RGBA", (w, h), (0, 0, 0, 0))
        result.paste(shadow, self.offset, shadow)
        result = PilImage.alpha_composite(result, source)
        return result


class Glow(Effect):
    """
    Add outer glow behind image content.

    Parameters
    ----------
    radius : int, optional
        Glow spread radius, by default 10
    color : Color, optional
        Glow color, by default "white"
    alpha : float, optional
        Glow opacity 0-1, by default 0.5

    """

    def __init__(
        self,
        radius: int = 10,
        color: Color = "white",
        alpha: float = 0.5,
    ) -> None:
        self.radius = radius
        self.alpha = alpha
        if isinstance(color, (int, str)):
            self.color = color
        else:
            self.color = tuple(color)

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        source = as_rgba(image)
        alpha_channel = source.split()[3]
        w, h = image.size

        color_rgba = to_rgba(self.color, alpha=int(self.alpha * 255))

        color_layer = PilImage.new("RGBA", (w, h), color_rgba)
        color_layer.putalpha(
            alpha_channel.point(lambda x: int(x * (color_rgba[3] / 255)))
        )

        if self.radius > 0:
            color_layer = color_layer.filter(
                ImageFilter.GaussianBlur(radius=self.radius)
            )

        result = PilImage.alpha_composite(color_layer, source)
        return result


class Gradient(Effect):
    """
    Fill image with linear gradient.

    Parameters
    ----------
    colors : list[Color]
        List of colors for gradient stops. Must be at least 2.
    direction : str, optional
        Gradient direction: "horizontal", "vertical", or "diagonal",
        by default "horizontal"

    """

    def __init__(
        self,
        colors: list[Color],
        direction: str = "horizontal",
    ) -> None:
        if len(colors) < 2:
            msg = "Gradient requires at least 2 colors"
            raise ValueError(msg)
        self.colors = colors
        self.direction = direction

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        w, h = image.size
        source = as_rgba(image)

        # LUT interpolates the stops uniformly, matching the old per-line
        # idx/lerp math where position runs 0..1 across the axis.
        lut = build_lut(self.colors)
        xs = np.arange(w, dtype=np.float64)
        ys = np.arange(h, dtype=np.float64)

        if self.direction == "vertical":
            t = (ys / h)[:, None] * np.ones((1, w))
        elif self.direction == "diagonal":
            t = (xs[None, :] + ys[:, None]) / (w + h)
        else:
            t = (xs / w)[None, :] * np.ones((h, 1))

        gradient = lut_from_t(t, lut)
        gradient[..., 3] = np.asarray(source.getchannel("A"))
        return from_array(gradient)


class PixelateRegion(Effect):
    """
    Pixelate a specific region of the image.

    Parameters
    ----------
    box : tuple[int, int, int, int]
        Region to pixelate (left, top, right, bottom).
    pixel_size : int, optional
        Size of each pixel block, by default 8

    """

    def __init__(self, box: tuple[int, int, int, int], pixel_size: int = 8) -> None:
        self.box = box
        self.pixel_size = pixel_size

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        result = as_rgba(image)
        left, top, right, bottom = self.box
        region = result.crop(self.box)
        rw = max(right - left, 1)
        rh = max(bottom - top, 1)
        ps = max(self.pixel_size, 1)

        small = region.resize(
            (max(rw // ps, 1), max(rh // ps, 1)),
            PilImage.Resampling.NEAREST,
        )
        pixelated = small.resize((rw, rh), PilImage.Resampling.NEAREST)
        result.paste(pixelated, (left, top))
        return result


class Noise(Effect):
    """
    Add film grain / noise overlay.

    Parameters
    ----------
    intensity : float, optional
        Noise strength 0-1, by default 0.15
    monochrome : bool, optional
        Single-channel noise vs color noise, by default True

    """

    def __init__(self, intensity: float = 0.15, monochrome: bool = True) -> None:
        self.intensity = min(1.0, max(0.0, intensity))
        self.monochrome = monochrome

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        w, h = image.size
        sigma = 32

        if self.monochrome:
            noise = PilImage.effect_noise((w, h), sigma).convert("L")
            noise = noise.convert("RGB")
        else:
            r = PilImage.effect_noise((w, h), sigma).convert("L")
            g = PilImage.effect_noise((w, h), sigma).convert("L")
            b = PilImage.effect_noise((w, h), sigma).convert("L")
            noise = PilImage.merge("RGB", (r, g, b))

        noise = noise.convert("RGBA")
        return PilImage.blend(as_rgba(image), noise, self.intensity)


class Posterize(Effect):
    """
    Reduce color levels (posterization effect).

    Parameters
    ----------
    bits : int, optional
        Bits per channel (1-8), lower = more posterized, by default 4

    """

    def __init__(self, bits: int = 4) -> None:
        self.bits = max(1, min(8, bits))

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        img = as_rgba(image)
        alpha = img.split()[3]
        posterized = ImageOps.posterize(img.convert("RGB"), self.bits)
        return PilImage.merge("RGBA", (*posterized.split(), alpha))


class Solarize(Effect):
    """
    Invert pixels above brightness threshold.

    Parameters
    ----------
    threshold : int, optional
        Brightness cutoff 0-255, by default 128

    """

    def __init__(self, threshold: int = 128) -> None:
        self.threshold = max(0, min(255, threshold))

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        img = as_rgba(image)
        alpha = img.split()[3]
        solarized = ImageOps.solarize(img.convert("RGB"), self.threshold)
        return PilImage.merge("RGBA", (*solarized.split(), alpha))


class Threshold(Effect):
    """
    Convert image to pure black and white at cutoff.

    Parameters
    ----------
    cutoff : int, optional
        Brightness cutoff 0-255, by default 128

    """

    def __init__(self, cutoff: int = 128) -> None:
        self.cutoff = max(0, min(255, cutoff))

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        grey = image.convert("L")
        bw = grey.point(lambda x: 255 if x > self.cutoff else 0)  # type: ignore[operator]
        return bw.convert("RGBA")


class OilPaint(Effect):
    """
    Simulate oil painting effect.

    Parameters
    ----------
    radius : int, optional
        Brush size, by default 3

    """

    def __init__(self, radius: int = 3) -> None:
        self.size = max(1, radius) * 2 + 1

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        return as_rgba(image).filter(ImageFilter.ModeFilter(size=self.size))


class TiltShift(Effect):
    """
    Gradient blur simulating shallow depth of field.

    Parameters
    ----------
    blur_strength : int, optional
        Blur amount at edges, by default 10
    focus_center : float, optional
        Vertical center of focus 0-1, by default 0.5
    focus_width : float, optional
        Height of sharp zone 0-1, by default 0.3

    """

    def __init__(
        self,
        blur_strength: int = 10,
        focus_center: float = 0.5,
        focus_width: float = 0.3,
    ) -> None:
        self.blur_strength = blur_strength
        self.focus_center = focus_center
        self.focus_width = focus_width

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        img = as_rgba(image)
        blurred = img.filter(ImageFilter.GaussianBlur(radius=self.blur_strength))
        w, h = img.size

        cy = int(h * self.focus_center)
        half_focus = int(h * self.focus_width / 2)

        mask = PilImage.new("L", (w, h), 0)
        draw = ImageDraw.Draw(mask)

        for y in range(h):
            if y <= cy - half_focus:
                val = int(255 * (1 - (y / max(cy - half_focus, 1))))
            elif y >= cy + half_focus:
                val = int(255 * ((y - cy - half_focus) / max(h - cy - half_focus, 1)))
            else:
                val = 0
            val = max(0, min(255, val))
            draw.line([(0, y), (w, y)], fill=val)

        result = PilImage.composite(blurred, img, mask)
        return result


class Duotone(Effect):
    """
    Map shadows to one color and highlights to another.

    Parameters
    ----------
    dark_color : Color, optional
        Color for shadows, by default (10, 10, 50)
    light_color : Color, optional
        Color for highlights, by default (255, 240, 200)

    """

    def __init__(
        self,
        dark_color: Color = (10, 10, 50),
        light_color: Color = (255, 240, 200),
    ) -> None:
        self.dark_color = dark_color
        self.light_color = light_color

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        grey = image.convert("L")
        dark = to_rgb(self.dark_color)
        light = to_rgb(self.light_color)
        result = ImageOps.colorize(grey, black=dark, white=light)
        return result.convert("RGBA")


class Bloom(Effect):
    """
    Make bright areas glow outward.

    Parameters
    ----------
    threshold : int, optional
        Brightness threshold 0-255, by default 200
    radius : int, optional
        Glow spread radius, by default 15
    intensity : float, optional
        Glow strength 0-1, by default 0.4

    """

    def __init__(
        self,
        threshold: int = 200,
        radius: int = 15,
        intensity: float = 0.4,
    ) -> None:
        self.threshold = max(0, min(255, threshold))
        self.radius = radius
        self.intensity = min(1.0, max(0.0, intensity))

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        img = as_rgba(image)
        lum = img.convert("L")
        bright_mask = lum.point(lambda x: 255 if x > self.threshold else 0)  # type: ignore[operator]

        blank = PilImage.new("RGBA", img.size, (0, 0, 0, 0))
        bright_parts = PilImage.composite(img, blank, bright_mask)

        if self.radius > 0:
            bright_parts = bright_parts.filter(
                ImageFilter.GaussianBlur(radius=self.radius)
            )

        return PilImage.blend(img, bright_parts, self.intensity)


class ChromaticAberration(Effect):
    """
    RGB channel offset for glitch/aberration effect.

    Parameters
    ----------
    offset : int, optional
        Pixel offset between channels, by default 4

    """

    def __init__(self, offset: int = 4) -> None:
        self.offset = offset

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        img = as_rgba(image)
        w, h = img.size
        r, g, b, a = img.split()

        zero = PilImage.new("L", (w, h), 0)
        r_img = PilImage.merge("RGBA", (r, zero, zero, a))
        g_img = PilImage.merge("RGBA", (zero, g, zero, a))
        b_img = PilImage.merge("RGBA", (zero, zero, b, a))

        result = PilImage.new("RGBA", (w, h), (0, 0, 0, 0))
        result.paste(r_img, (self.offset, -self.offset), r_img)
        result.paste(g_img, (0, 0), g_img)
        result.paste(b_img, (-self.offset, self.offset), b_img)

        return result


class EdgeGlow(Effect):
    """
    Neon-like edge highlight.

    Parameters
    ----------
    color : Color, optional
        Edge glow color, by default "cyan"
    intensity : float, optional
        Glow strength 0-1, by default 0.8

    """

    def __init__(self, color: Color = "cyan", intensity: float = 0.8) -> None:
        self.color = color
        self.intensity = min(1.0, max(0.0, intensity))

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        img = as_rgba(image)
        grey = img.convert("L")
        edges = grey.filter(ImageFilter.FIND_EDGES)

        c = to_rgb(self.color)
        colored = ImageOps.colorize(edges, black=(0, 0, 0), white=c).convert("RGBA")

        return PilImage.blend(img, colored, self.intensity)


class Halftone(Effect):
    """
    Comic-book dot pattern effect.

    Parameters
    ----------
    dot_size : int, optional
        Size of halftone dots, by default 8
    angle : float, optional
        Screen angle in degrees, by default 45.0

    """

    def __init__(self, dot_size: int = 8, angle: float = 45.0) -> None:
        self.dot_size = max(2, dot_size)
        self.angle = angle

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        grey = image.convert("L")
        w, h = grey.size
        out = PilImage.new("RGBA", (w, h), "white")
        draw = ImageDraw.Draw(out)
        ds = self.dot_size

        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        # Block averages in one C op: shrink to the block grid (area average).
        nx = (w + ds - 1) // ds
        ny = (h + ds - 1) // ds
        small = grey.resize((nx, ny), PilImage.Resampling.BOX)
        block_avg = np.asarray(small)

        for j in range(ny):
            for i in range(nx):
                avg = block_avg[j, i] / 255.0
                radius = (1.0 - avg) * (ds / 2)

                if radius > 0.5:
                    cx = i * ds + ds // 2
                    cy = j * ds + ds // 2
                    rx = abs(radius * cos_a)
                    ry = abs(radius * sin_a)
                    draw.ellipse(
                        [cx - rx, cy - ry, cx + rx, cy + ry],
                        fill="black",
                    )

        return out


class Kaleidoscope(Effect):
    """
    Mirror-tile symmetry effect.

    Parameters
    ----------
    segments : int, optional
        Number of reflective segments, by default 8

    """

    def __init__(self, segments: int = 8) -> None:
        self.segments = max(3, segments)

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        w, h = image.size
        cx, cy = w // 2, h // 2
        size = min(cx, cy)
        img = as_rgba(image)
        center = img.crop((cx - size, cy - size, cx + size, cy + size))

        result = PilImage.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
        angle_step = 360.0 / self.segments

        for i in range(self.segments):
            rotated = center.rotate(i * angle_step, expand=False, center=(size, size))
            result = PilImage.alpha_composite(result, rotated)

        final = img.copy()
        final.paste(result, (cx - size, cy - size), result)
        return final


class Ripple(Effect):
    """
    Water-like wave distortion.

    Parameters
    ----------
    amplitude : int, optional
        Wave height in pixels, by default 5
    period : int, optional
        Wave length in pixels, by default 50

    """

    def __init__(self, amplitude: int = 5, period: int = 50) -> None:
        self.amplitude = amplitude
        self.period = max(1, period)

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        w, h = image.size
        arr = np.asarray(as_rgba(image))

        rows = np.arange(h)
        dxs = (self.amplitude * np.sin(2 * np.pi * rows / self.period)).astype(int)

        sx = np.arange(w)[None, :] + dxs[:, None]
        valid = (sx >= 0) & (sx < w)
        ys = np.broadcast_to(rows[:, None], (h, w))

        out = np.zeros_like(arr)
        out[valid] = arr[ys[valid], np.clip(sx, 0, w - 1)[valid]]
        return from_array(out)


class Blur(Effect):
    """
    Apply box or gaussian blur.

    Parameters
    ----------
    amount : float, optional
        Blur radius, by default 1
    mode : Literal["box", "gaussian"], optional
        Blur type, by default "gaussian"

    """

    def __init__(self, amount: float = 1, *, mode: str = "gaussian") -> None:
        self.amount = amount
        self.mode = mode

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        img = as_rgba(image)
        if self.mode == "box":
            return img.filter(ImageFilter.BoxBlur(radius=self.amount))
        return img.filter(ImageFilter.GaussianBlur(radius=self.amount))


class Contour(Effect):
    """Find image contours. Built-in Pillow filter."""

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        return as_rgba(image).filter(ImageFilter.CONTOUR)


class Emboss(Effect):
    """Emboss effect. Built-in Pillow filter."""

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        return as_rgba(image).filter(ImageFilter.EMBOSS)


class EdgeEnhance(Effect):
    """
    Enhance image edges.

    Parameters
    ----------
    amount : int, optional
        Number of enhancement passes, by default 1

    """

    def __init__(self, amount: int = 1) -> None:
        self.amount = amount

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        img = as_rgba(image)
        for _ in range(self.amount):
            img = img.filter(ImageFilter.EDGE_ENHANCE)
        return img


class Sharpen(Effect):
    """
    Sharpen image.

    Parameters
    ----------
    amount : int, optional
        Number of sharpen passes, by default 1

    """

    def __init__(self, amount: int = 1) -> None:
        self.amount = amount

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        img = as_rgba(image)
        for _ in range(self.amount):
            img = img.filter(ImageFilter.SHARPEN)
        return img


class Smooth(Effect):
    """
    Smooth image.

    Parameters
    ----------
    amount : int, optional
        Number of smoothing passes, by default 1

    """

    def __init__(self, amount: int = 1) -> None:
        self.amount = amount

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        img = as_rgba(image)
        for _ in range(self.amount):
            img = img.filter(ImageFilter.SMOOTH)
        return img


class Grayscale(Effect):
    """Convert image to grayscale."""

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        return image.convert("L").convert("RGBA")


class Sepia(Effect):
    """Apply sepia tone effect."""

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        grey = image.convert("L")
        return ImageOps.colorize(grey, black="#704214", white="#F5E6C8").convert("RGBA")


class Invert(Effect):
    """Invert image colors."""

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        return ImageOps.invert(image.convert("RGB")).convert("RGBA")


class Pixelate(Effect):
    """
    Pixelate entire image.

    Parameters
    ----------
    pixel_size : int, optional
        Size of pixel blocks, by default 8

    """

    def __init__(self, pixel_size: int = 8) -> None:
        self.pixel_size = max(1, pixel_size)

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        w, h = image.size
        ps = self.pixel_size
        small = image.resize(
            (max(w // ps, 1), max(h // ps, 1)),
            PilImage.Resampling.NEAREST,
        )
        return small.resize((w, h), PilImage.Resampling.NEAREST)


class Glitch(Effect):
    """
    VHS-style glitch effect with strip offsets and channel bleed.

    Parameters
    ----------
    amount : float, optional
        Glitch intensity 0-1, by default 0.5
    seed : int | None, optional
        Seed for reproducible output. If None (default), output is random.

    """

    def __init__(self, amount: float = 0.5, seed: int | None = None) -> None:
        self.amount = max(0.0, min(1.0, amount))
        self.seed = seed

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        import random as _random

        rng = _random.Random(self.seed)

        src = np.asarray(as_rgba(image))
        h, w = src.shape[:2]
        res = src.copy()
        strip_h = max(2, int(h * 0.04 * self.amount))

        y = 0
        while y < h:
            if rng.random() < 0.25 * self.amount:
                sh = min(strip_h, h - y)
                offset = int((rng.randint(-15, 15)) * self.amount)
                if offset >= 0 and w - offset > 0:
                    res[y : y + sh, : w - offset] = src[y : y + sh, offset:w]
                elif offset < 0 and w + offset > 0:
                    res[y : y + sh, -offset:w] = src[y : y + sh, : w + offset]
                y += sh
            else:
                y += 1

        return from_array(res)


class Sketch(Effect):
    """
    Pencil drawing effect using dodge blend.

    Parameters
    ----------
    blur : int, optional
        Stroke softness, by default 5

    """

    def __init__(self, blur: int = 5) -> None:
        self.blur = blur

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        grey = image.convert("L")
        inverted = ImageOps.invert(grey)
        blurred = inverted.filter(ImageFilter.GaussianBlur(radius=self.blur))

        g = np.asarray(grey).astype(np.int32)
        b = np.asarray(blurred).astype(np.int32)
        d = g * 256 // np.maximum(1, 256 - b)
        out = np.minimum(255, d).astype(np.uint8)
        return PilImage.fromarray(out, "L").convert("RGBA")


class Cartoon(Effect):
    """
    Cartoon effect with quantized colors and bold edges.

    Parameters
    ----------
    colors : int, optional
        Bits per channel 1-8, by default 5
    edge_thickness : int, optional
        Edge line width, by default 1

    """

    def __init__(self, colors: int = 5, edge_thickness: int = 1) -> None:
        self.colors = max(1, min(8, colors))
        self.edge_thickness = max(0, edge_thickness)

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        img = as_rgba(image)
        posterized = ImageOps.posterize(img.convert("RGB"), self.colors)
        grey = img.convert("L")
        edges = grey.filter(ImageFilter.FIND_EDGES)
        edges = ImageOps.invert(edges)

        if self.edge_thickness > 0:
            size = self.edge_thickness * 2 + 1
            edges = edges.filter(ImageFilter.MaxFilter(size))

        posterized = posterized.convert("RGBA")
        edge_layer = ImageOps.colorize(edges, black=(0, 0, 0), white=(0, 0, 0)).convert(
            "RGBA"
        )
        edge_layer.putalpha(edges)

        return PilImage.alpha_composite(edge_layer, posterized)


class Thermal(Effect):
    """
    Map brightness to thermal/infrared color ramp.

    """

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        grey = image.convert("L")
        palette = []
        for i in range(256):
            t = i / 255.0
            if t < 0.25:
                r, g, b = 0, 0, int(t * 4 * 200)
            elif t < 0.5:
                r, g, b = 0, int((t - 0.25) * 4 * 200), 200 - int((t - 0.25) * 4 * 200)
            elif t < 0.75:
                r, g, b = int((t - 0.5) * 4 * 255), 200 - int((t - 0.5) * 4 * 100), 0
            else:
                r, g, b = (
                    255,
                    100 + int((t - 0.75) * 4 * 155),
                    int((t - 0.75) * 4 * 100),
                )
            palette.extend([r, g, b])

        palette += [0] * (768 - len(palette))
        pal_img = grey.convert("P")
        pal_img.putpalette(palette)
        return pal_img.convert("RGBA")


class Dither(Effect):
    """
    Ordered Bayer dithering for retro 1-bit look.

    Parameters
    ----------
    threshold : int, optional
        Brightness threshold 0-255, by default 128

    """

    def __init__(self, threshold: int = 128) -> None:
        self.threshold = max(0, min(255, threshold))

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        grey = image.convert("L")
        bayer = [
            [0, 48, 12, 60, 3, 51, 15, 63],
            [32, 16, 44, 28, 35, 19, 47, 31],
            [8, 56, 4, 52, 11, 59, 7, 55],
            [40, 24, 36, 20, 43, 27, 39, 23],
            [2, 50, 14, 62, 1, 49, 13, 61],
            [34, 18, 46, 30, 33, 17, 45, 29],
            [10, 58, 6, 54, 9, 57, 5, 53],
            [42, 26, 38, 22, 41, 25, 37, 21],
        ]
        w, h = grey.size
        g = np.asarray(grey)
        bayer_arr = np.array(bayer, dtype=np.float64)
        reps_y = (h + 7) // 8
        reps_x = (w + 7) // 8
        tiled = np.tile(bayer_arr, (reps_y, reps_x))[:h, :w]
        thresh = (tiled + 0.5) * 255 / 64
        out = np.where(g > thresh, 255, 0).astype(np.uint8)
        return PilImage.fromarray(out, "L").convert("RGBA")


class Scanlines(Effect):
    """
    CRT scanline overlay.

    Parameters
    ----------
    size : int, optional
        Scanline thickness, by default 3
    opacity : float, optional
        Darkness 0-1, by default 0.3

    """

    def __init__(self, size: int = 3, opacity: float = 0.3) -> None:
        self.size = max(1, size)
        self.opacity = max(0.0, min(1.0, opacity))

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        img = as_rgba(image)
        w, h = img.size
        overlay = PilImage.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        step = self.size * 2
        alpha = int(255 * self.opacity)
        for y in range(0, h, step):
            draw.rectangle([(0, y), (w, y + self.size - 1)], fill=(0, 0, 0, alpha))
        return PilImage.alpha_composite(img, overlay)


class Vortex(Effect):
    """
    Swirl distortion effect.

    Parameters
    ----------
    strength : float, optional
        Swirl intensity, by default 3.0
    radius : float, optional
        Swirl radius in pixels. Defaults to half the image.

    """

    def __init__(self, strength: float = 3.0, radius: float | None = None) -> None:
        self.strength = strength
        self.radius = radius

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        img = as_rgba(image)
        w, h = img.size
        cx, cy = w // 2, h // 2
        mr = self.radius if self.radius is not None else min(cx, cy)
        arr = np.asarray(img)

        ys, xs = np.mgrid[0:h, 0:w]
        dx = xs - cx
        dy = ys - cy
        dist = np.sqrt(dx * dx + dy * dy)
        mask = (dist < mr) & (dist > 0.5)

        angle = self.strength * (1 - dist / mr)
        cs = np.cos(angle)
        sn = np.sin(angle)
        nx = (cx + dx * cs - dy * sn).astype(int)
        ny = (cy + dx * sn + dy * cs).astype(int)

        inb = mask & (nx >= 0) & (nx < w) & (ny >= 0) & (ny < h)
        out = arr.copy()
        out[inb] = arr[np.clip(ny, 0, h - 1)[inb], np.clip(nx, 0, w - 1)[inb]]
        return from_array(out)


class Neon(Effect):
    """
    Cyberpunk neon edge glow on dark background.

    Parameters
    ----------
    color : Color, optional
        Glow color, by default "cyan"
    glow_radius : int, optional
        Glow spread, by default 5

    """

    def __init__(self, color: Color = "cyan", glow_radius: int = 5) -> None:
        self.color = color
        self.glow_radius = max(0, glow_radius)

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        img = as_rgba(image)
        grey = img.convert("L")
        edges = grey.filter(ImageFilter.FIND_EDGES)

        white: str | tuple[int, ...] = (
            self.color if isinstance(self.color, (str, tuple, int)) else (0, 255, 255)
        )  # type: ignore[assignment]
        colored = ImageOps.colorize(edges, black=(0, 0, 0), white=white).convert("RGBA")
        colored.putalpha(edges)

        if self.glow_radius > 0:
            colored = colored.filter(ImageFilter.GaussianBlur(radius=self.glow_radius))

        bg = PilImage.blend(img, PilImage.new("RGBA", img.size, (0, 0, 0, 0)), 0.5)
        return PilImage.alpha_composite(colored, bg)


class PixelSort(Effect):
    """
    Glitch-art pixel sorting effect.

    Parameters
    ----------
    direction : str, optional
        Sort direction: "horizontal" or "vertical", by default "horizontal"

    """

    def __init__(self, direction: str = "horizontal") -> None:
        self.direction = direction

    @staticmethod
    def _brightness(p: tuple[int, ...]) -> float:
        return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]

    def apply(self, image: PilImage.Image) -> PilImage.Image:
        arr = np.asarray(as_rgba(image))
        rgb = arr[..., :3].astype(np.float64)
        bright = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]

        axis = 0 if self.direction == "vertical" else 1
        order = np.argsort(bright, axis=axis, kind="stable")
        out = np.take_along_axis(arr, order[..., None], axis=axis)
        return from_array(out)
