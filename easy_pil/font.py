"""Font module for loading and caching fonts."""

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from PIL import ImageFont

fonts_directory = Path(__file__).parent / "fonts"


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
