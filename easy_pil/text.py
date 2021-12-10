from typing import Tuple, Union

from PIL import ImageFont


class Text:
    """Text class

    :param text: Text 
    :type text: str
    :param font: Font for text
    :type font: ImageFont.FreeTypeFont
    :param color: Font color, defaults to "black"
    :type color: Union[Tuple[int, int, int], str, int], optional
    """
    def __init__(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        color: Union[Tuple[int, int, int], str, int] = "black",
    ) -> None:
        self.text = text
        self.font = font
        self.color = color
