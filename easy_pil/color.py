"""Unified color normalization helpers.

Centralizes the ad-hoc color parsing that the various effects used to
reimplement. A color may be given as an ``int`` (``0xRRGGBB``), a string
name/hex understood by :func:`PIL.ImageColor.getrgb`, an RGB 3-tuple, or an
RGBA 4-tuple. These helpers normalize any of those into concrete tuples.
"""

from __future__ import annotations

from PIL.ImageColor import getrgb

from .canvas import Color

__all__ = ["to_rgb", "to_rgba"]


def _clamp(value: int) -> int:
    """Clamp an integer channel value into the 0-255 range."""
    return max(0, min(255, int(value)))


def to_rgba(color: Color, *, alpha: int = 255) -> tuple[int, int, int, int]:
    """
    Normalize any supported color into an RGBA 4-tuple.

    Parameters
    ----------
    color : Color
        Color as ``int`` (``0xRRGGBB``), string name/hex, RGB 3-tuple, or
        RGBA 4-tuple.
    alpha : int, optional
        Alpha applied when the color carries no explicit alpha channel
        (strings without alpha, ints, and 3-tuples), by default 255. An
        explicit 4-tuple alpha always takes precedence.

    Returns
    -------
    tuple[int, int, int, int]
        The color as ``(r, g, b, a)`` with every channel clamped to 0-255.

    """
    if isinstance(color, str):
        parsed = getrgb(color)
        if len(parsed) >= 4:
            r, g, b, a = parsed[0], parsed[1], parsed[2], parsed[3]
        else:
            r, g, b, a = parsed[0], parsed[1], parsed[2], alpha
    elif isinstance(color, int):
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        a = alpha
    else:
        seq = tuple(color)
        if len(seq) >= 4:
            r, g, b, a = seq[0], seq[1], seq[2], seq[3]
        else:
            r, g, b = seq[0], seq[1], seq[2]
            a = alpha

    return (_clamp(r), _clamp(g), _clamp(b), _clamp(a))


def to_rgb(color: Color) -> tuple[int, int, int]:
    """
    Normalize any supported color into an RGB 3-tuple, dropping alpha.

    Parameters
    ----------
    color : Color
        Color as ``int`` (``0xRRGGBB``), string name/hex, RGB 3-tuple, or
        RGBA 4-tuple.

    Returns
    -------
    tuple[int, int, int]
        The color as ``(r, g, b)`` with every channel clamped to 0-255.

    """
    r, g, b, _ = to_rgba(color)
    return (r, g, b)
