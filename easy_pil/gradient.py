"""Gradient fill types for shapes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence, cast

import numpy as np
from PIL import Image as PilImage
from PIL.ImageColor import getrgb

from easy_pil._nputil import build_lut, from_array, lut_from_t

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
        lut = build_lut(self.colors)
        xs = np.arange(width, dtype=np.float64)
        ys = np.arange(height, dtype=np.float64)

        if self.direction == "vertical":
            hm = max(height - 1, 1)
            t = (ys / hm)[:, None] * np.ones((1, width))
        elif self.direction == "diagonal":
            denom = max(width + height - 2, 1)
            t = (xs[None, :] + ys[:, None]) / denom
        else:  # horizontal
            wm = max(width - 1, 1)
            t = (xs / wm)[None, :] * np.ones((height, 1))

        return from_array(lut_from_t(t, lut))


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

        lut = build_lut(self.colors)
        xs = np.arange(width, dtype=np.float64) - cx
        ys = np.arange(height, dtype=np.float64) - cy
        dist = np.hypot(xs[None, :], ys[:, None])
        t = np.clip(dist / max_dist, 0.0, 1.0)

        return from_array(lut_from_t(t, lut))
