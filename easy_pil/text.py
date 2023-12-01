from typing import Tuple, Union

from PIL import ImageFont

from .font import Font


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
        font: Union[ImageFont.FreeTypeFont, Font],
        color: Union[
            int, str, Tuple[int, int, int], Tuple[int, int, int, int]
        ] = "black",
    ) -> None:
        self.text = text
        self.color = color

        if isinstance(font, Font):
            self.font = font.font
        else:
            self.font = font

    def getsize(self):
        bbox = self.font.getbbox(self.text)
        return bbox[2], bbox[3]
