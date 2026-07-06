"""Internal numpy helpers shared by the vectorized render paths.

These keep the per-pixel work in C: convert between PIL images and numpy
arrays, build a color lookup table from gradient stops, and guard against
redundant ``convert("RGBA")`` copies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PIL import Image as PilImage
from PIL.ImageColor import getrgb

if TYPE_CHECKING:
    from collections.abc import Sequence

ColorLike = str | int | tuple[int, ...]


def as_rgba(image: PilImage.Image) -> PilImage.Image:
    """Return an RGBA image, avoiding a copy when already RGBA."""
    return image if image.mode == "RGBA" else image.convert("RGBA")


def to_array(image: PilImage.Image) -> np.ndarray:
    """Return the image pixels as an ``(H, W, C)`` uint8 array."""
    return np.asarray(image)


def from_array(arr: np.ndarray, mode: str = "RGBA") -> PilImage.Image:
    """Build a PIL image from an array, ensuring contiguous uint8 data."""
    return PilImage.fromarray(np.ascontiguousarray(arr, dtype=np.uint8), mode)


def parse_rgba(color: ColorLike, *, alpha: int = 255) -> tuple[int, int, int, int]:
    """Normalize a single color to an RGBA 4-tuple (0-255)."""
    if isinstance(color, str):
        result = getrgb(color)
        if len(result) == 3:
            return (result[0], result[1], result[2], alpha)
        return (result[0], result[1], result[2], result[3])
    if isinstance(color, int):
        return ((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF, alpha)
    if len(color) == 3:
        return (int(color[0]), int(color[1]), int(color[2]), alpha)
    return (int(color[0]), int(color[1]), int(color[2]), int(color[3]))


def build_lut(colors: Sequence[ColorLike], n: int = 256) -> np.ndarray:
    """
    Build an ``(n, 4)`` uint8 lookup table interpolating the color stops.

    Index the table with a 0..n-1 array (t scaled to that range) to color a
    whole image in one vectorized gather instead of per-pixel interpolation.
    """
    stops = np.array([parse_rgba(c) for c in colors], dtype=np.float64)
    if len(stops) == 1:
        return np.tile(stops[0], (n, 1)).astype(np.uint8)

    # Position of each stop along 0..1, and the query positions for the LUT.
    stop_pos = np.linspace(0.0, 1.0, len(stops))
    query = np.linspace(0.0, 1.0, n)
    lut = np.empty((n, 4), dtype=np.float64)
    for ch in range(4):
        lut[:, ch] = np.interp(query, stop_pos, stops[:, ch])
    return np.rint(lut).astype(np.uint8)


def lut_from_t(t: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """Map a float ``t`` array in [0, 1] to RGBA pixels via ``lut``."""
    n = lut.shape[0]
    idx = np.clip(np.rint(t * (n - 1)), 0, n - 1).astype(np.intp)
    return lut[idx]
