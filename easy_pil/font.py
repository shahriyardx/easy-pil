"""Font module for loading and caching fonts."""

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from PIL import ImageDraw, ImageFont

fonts_directory = Path(__file__).parent / "fonts"

# A plane-15 private-use codepoint that essentially no font maps to a real
# glyph. Rendering it therefore yields the font's ``.notdef`` ("tofu") glyph,
# which we use as a reference to detect characters the font cannot render.
_NOTDEF_SENTINEL = "\U000f0000"

# Keyword arguments understood by ``ImageDraw.textbbox`` so that
# ``draw_text_with_fallback`` can forward only the ones it accepts.
_BBOX_KEYS = frozenset(
    {
        "spacing",
        "align",
        "direction",
        "features",
        "language",
        "stroke_width",
        "embedded_color",
    }
)

# Keyword arguments understood by ``ImageDraw.textlength``.
_LENGTH_KEYS = frozenset({"direction", "features", "language", "embedded_color"})


def _glyph_repr(
    font: ImageFont.FreeTypeFont, char: str
) -> tuple[tuple[int, int], bytes]:
    """
    Return a hashable representation of a single glyph's rendered mask.

    Parameters
    ----------
    font : ImageFont.FreeTypeFont
        Font used to render the glyph.
    char : str
        Character to render.

    Returns
    -------
    tuple[tuple[int, int], bytes]
        The mask size and its raw bytes (empty bytes for an empty mask).

    """
    mask = font.getmask(char)
    size = mask.size
    if size == (0, 0):
        return (size, b"")
    return (size, bytes(mask))


def _font_can_render(font: ImageFont.FreeTypeFont, char: str) -> bool:
    """
    Return whether ``font`` has a real (non-``.notdef``) glyph for ``char``.

    Whitespace and empty strings are always considered renderable. Any other
    character whose rendered glyph is identical to the font's ``.notdef`` glyph
    is considered missing.

    Parameters
    ----------
    font : ImageFont.FreeTypeFont
        Font to query.
    char : str
        Character to test.

    Returns
    -------
    bool
        True if the font can render the character.

    """
    if not char or char.isspace():
        return True
    return _glyph_repr(font, char) != _glyph_repr(font, _NOTDEF_SENTINEL)


fonts_path = {
    "caveat": {
        "regular": str(fonts_directory / "caveat" / "caveat.ttf"),
        "bold": str(fonts_directory / "caveat" / "caveat.ttf"),
        "italic": str(fonts_directory / "caveat" / "caveat.ttf"),
        "light": str(fonts_directory / "caveat" / "caveat.ttf"),
    },
    "montserrat": {
        "regular": str(fonts_directory / "montserrat" / "montserrat_regular.ttf"),
        "bold": str(fonts_directory / "montserrat" / "montserrat_bold.ttf"),
        "italic": str(fonts_directory / "montserrat" / "montserrat_italic.ttf"),
        "light": str(fonts_directory / "montserrat" / "montserrat_light.ttf"),
    },
    "poppins": {
        "regular": str(fonts_directory / "poppins" / "poppins_regular.ttf"),
        "bold": str(fonts_directory / "poppins" / "poppins_bold.ttf"),
        "italic": str(fonts_directory / "poppins" / "poppins_italic.ttf"),
        "light": str(fonts_directory / "poppins" / "poppins_light.ttf"),
    },
}


class Font:
    """
    Font class.

    Parameters
    ----------
    path : str
        Path of font
    size : int, optional
        Size of font, by default 10

    """

    def __init__(self, path: str, size: int = 10, **kwargs: Any) -> None:
        """Initialize Font instance."""
        self.font = ImageFont.truetype(path, size=size, **kwargs)

    @classmethod
    def load(cls, path: str, size: int = 10, **kwargs: Any) -> "Font":
        """
        Convenience constructor for a :class:`Font`.

        Parameters
        ----------
        path : str
            Path of font.
        size : int, optional
            Size of font, by default 10.
        **kwargs : Any
            Extra keyword arguments forwarded to ``ImageFont.truetype``.

        Returns
        -------
        Font
            The loaded font.

        """
        return cls(path, size, **kwargs)

    def can_render(self, char: str) -> bool:
        """
        Return whether the font has a real glyph for ``char``.

        Whitespace (and the empty string) always returns True. Any other
        character that would fall back to the font's ``.notdef`` glyph returns
        False.

        Parameters
        ----------
        char : str
            Character to test.

        Returns
        -------
        bool
            True if the font can render the character.

        """
        return _font_can_render(self.font, char)

    def getsize(self, text: str) -> tuple[float, float]:
        """
        Get the width and height of the text.

        Returns
        -------
        tuple[float, float]
            Width and height of the text bounding box.

        """
        bbox = self.font.getbbox(text)
        return bbox[2], bbox[3]

    @staticmethod
    @lru_cache(32)
    def poppins(
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ) -> ImageFont.FreeTypeFont:
        """
        Poppins font.

        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10

        """
        return ImageFont.truetype(fonts_path["poppins"][variant], size=size)

    @staticmethod
    @lru_cache(32)
    def caveat(
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ) -> ImageFont.FreeTypeFont:
        """
        Caveat font.

        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10

        """
        return ImageFont.truetype(fonts_path["caveat"][variant], size=size)

    @staticmethod
    @lru_cache(32)
    def montserrat(
        variant: Literal["regular", "bold", "italic", "light"] = "regular",
        size: int = 10,
    ) -> ImageFont.FreeTypeFont:
        """
        Montserrat font.

        Parameters
        ----------
        variant : Literal["regular", "bold", "italic", "light"], optional
            Font variant, by default "regular"
        size : int, optional
            Font size, by default 10

        """
        return ImageFont.truetype(fonts_path["montserrat"][variant], size=size)


def draw_text_with_fallback(
    draw: ImageDraw.ImageDraw,
    position: tuple[float, float],
    text: str,
    fonts: list[ImageFont.FreeTypeFont],
    *,
    fill: Any = "black",
    anchor: str | None = None,
    **kwargs: Any,
) -> tuple[int, int, int, int]:
    """
    Draw ``text`` using a chain of fonts, falling back per character.

    The text is split into runs of consecutive characters, where each run is
    drawn with the first font in ``fonts`` that can render its characters. This
    allows text mixing glyphs from different fonts (for example Latin text with
    emoji or CJK) to render correctly. Characters that no font can render are
    drawn with the primary (first) font, producing its ``.notdef`` glyph.

    Parameters
    ----------
    draw : ImageDraw.ImageDraw
        Drawing context to render onto.
    position : tuple[float, float]
        Top-left ``(x, y)`` position of the text.
    text : str
        Text to draw.
    fonts : list[ImageFont.FreeTypeFont]
        Fonts to use, primary first, fallbacks after. Must be non-empty.
    fill : Any, optional
        Fill colour, by default ``"black"``.
    anchor : str | None, optional
        Text anchor forwarded to the drawing calls, by default None. Only
        left-based anchors behave correctly when more than one run is drawn.
    **kwargs : Any
        Extra keyword arguments forwarded to ``ImageDraw.text``. Measurement
        related keys are also forwarded to the bounding-box calculation.

    Returns
    -------
    tuple[int, int, int, int]
        The union bounding box ``(left, top, right, bottom)`` of everything
        drawn, in absolute image coordinates.

    """
    if not fonts:
        raise ValueError("`fonts` must contain at least one font")

    x, y = position
    if not text:
        ix, iy = int(x), int(y)
        return (ix, iy, ix, iy)

    bbox_kwargs = {k: v for k, v in kwargs.items() if k in _BBOX_KEYS}
    length_kwargs = {k: v for k, v in kwargs.items() if k in _LENGTH_KEYS}

    def pick_font(char: str) -> ImageFont.FreeTypeFont:
        for font in fonts:
            if _font_can_render(font, char):
                return font
        return fonts[0]

    # Group consecutive characters that resolve to the same font into runs.
    runs: list[tuple[ImageFont.FreeTypeFont, str]] = []
    for char in text:
        font = pick_font(char)
        if runs and runs[-1][0] is font:
            runs[-1] = (font, runs[-1][1] + char)
        else:
            runs.append((font, char))

    bbox: tuple[int, int, int, int] | None = None
    cursor = x
    for font, run in runs:
        draw.text((cursor, y), run, font=font, fill=fill, anchor=anchor, **kwargs)
        run_bbox = draw.textbbox(
            (cursor, y), run, font=font, anchor=anchor, **bbox_kwargs
        )
        if bbox is None:
            bbox = run_bbox
        else:
            bbox = (
                min(bbox[0], run_bbox[0]),
                min(bbox[1], run_bbox[1]),
                max(bbox[2], run_bbox[2]),
                max(bbox[3], run_bbox[3]),
            )
        cursor += draw.textlength(run, font=font, **length_kwargs)

    return (int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]))
