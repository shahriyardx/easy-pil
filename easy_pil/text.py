from PIL import ImageFont
from typing import Union, Tuple


class Text:
    """Text class for making multicolor text"""

    def __init__(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        color: Union[Tuple[int, int, int], str, int] = "black",
    ) -> None:
        self.text = text
        self.font = font
        self.color = color
