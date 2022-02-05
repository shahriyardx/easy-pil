from typing import Tuple, Union

from PIL import ImageFont

from .color import Color

class Text:
    """Text class

    Parameters
    ----------
    text : str
        Text
    font : ImageFont.FreeTypeFont
        Font for text
    color : Color, optional
        Font color, by default "black"
    """

    def __init__(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        color: Color = "black",
    ) -> None:
        self.text = text
        self.font = font
        self.color = color
