"""Gradient fill types for shapes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence, cast

from PIL import Image as PilImage
from PIL.ImageColor import getrgb

ColorRGB = tuple[int, int, int]
ColorRGBA = tuple[int, int, int, int]


class Gradient(ABC):
    """Base class for gradient fills passed to Editor shape methods."""

    colors: list[ColorRGB | ColorRGBA | str]

    @abstractmethod
    def render(self, width: int, height: int) -> PilImage.Image:
        """Render gradient to RGBA image of given size."""
        ...

    def _parse(self, color: str | tuple[int, ...]) -> ColorRGBA:
        if isinstance(color, str):
            result = getrgb(color)
            if len(result) == 3:
                return (*result, 255)
            return cast(ColorRGBA, result)
        if len(color) == 3:
            return (*color, 255)
        return cast(ColorRGBA, tuple(color))

    def _color_at(self, t: float) -> ColorRGBA:
        cs = self.colors
        if t <= 0:
            return self._parse(cs[0])
        if t >= 1:
            return self._parse(cs[-1])

        n = len(cs) - 1
        seg = t * n
        idx = int(seg)
        local_t = seg - idx

        c1 = self._parse(cs[idx])
        c2 = self._parse(cs[min(idx + 1, n)])
        return cast(
            ColorRGBA,
            tuple(int(a + (b - a) * local_t) for a, b in zip(c1, c2, strict=False)),
        )


class LinearGradient(Gradient):
    """Linear gradient across a shape.

    Parameters
    ----------
    colors : Sequence[Color]
        Two or more colors to interpolate between.
    direction : str
        Gradient direction: "horizontal", "vertical", or "diagonal".
        Defaults to "horizontal".

    """

    def __init__(
        self,
        colors: Sequence[ColorRGB | ColorRGBA | str],
        direction: str = "horizontal",
    ) -> None:
        self.colors = list(colors)
        self.direction = direction

    def render(self, width: int, height: int) -> PilImage.Image:
        img = PilImage.new("RGBA", (width, height))
        pixels = img.load()
        assert pixels is not None
        wm = max(width - 1, 1)
        hm = max(height - 1, 1)

        if self.direction == "vertical":
            for y in range(height):
                t = y / hm
                c = self._color_at(t)
                for x in range(width):
                    pixels[x, y] = c
        elif self.direction == "diagonal":
            denom = max(width + height - 2, 1)
            for y in range(height):
                for x in range(width):
                    t = (x + y) / denom
                    pixels[x, y] = self._color_at(t)
        else:  # horizontal
            for y in range(height):
                for x in range(width):
                    t = x / wm
                    pixels[x, y] = self._color_at(t)

        return img


class RadialGradient(Gradient):
    """Radial gradient from center outward.

    Parameters
    ----------
    colors : Sequence[Color]
        Two or more colors, outermost last.
    center : tuple[float, float]
        Center as ratio of width/height (0-1). Defaults to (0.5, 0.5).

    """

    def __init__(
        self,
        colors: Sequence[ColorRGB | ColorRGBA | str],
        center: tuple[float, float] = (0.5, 0.5),
    ) -> None:
        self.colors = list(colors)
        self.center = center

    def render(self, width: int, height: int) -> PilImage.Image:
        img = PilImage.new("RGBA", (width, height))
        cx = int(width * self.center[0])
        cy = int(height * self.center[1])
        max_dist = (
            max(
                ((0 - cx) ** 2 + (0 - cy) ** 2) ** 0.5,
                ((width - cx) ** 2 + (0 - cy) ** 2) ** 0.5,
                ((0 - cx) ** 2 + (height - cy) ** 2) ** 0.5,
                ((width - cx) ** 2 + (height - cy) ** 2) ** 0.5,
            )
            or 1
        )

        pixels = img.load()
        assert pixels is not None
        for y in range(height):
            dy2 = (y - cy) ** 2
            for x in range(width):
                dist = ((x - cx) ** 2 + dy2) ** 0.5
                t = min(dist / max_dist, 1.0)
                pixels[x, y] = self._color_at(t)

        return img
