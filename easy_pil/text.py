from typing import Tuple, Union

from PIL import ImageFont


class Text:
    def __init__(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        color: Union[Tuple[int, int, int], str, int] = "black",
    ) -> None:
        """Text class

        :param text: Text 
        :type text: str
        :param font: Font for text
        :type font: ImageFont.FreeTypeFont
        :param color: Font color, defaults to "black"
        :type color: Union[Tuple[int, int, int], str, int], optional
        """
        self.text = text
        self.font = font
        self.color = color
