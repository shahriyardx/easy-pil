from typing import Tuple, Union

from PIL import ImageFont


class Text:
    """Text class

    Parameters
    ----------
    text : str
        Text
    font : ImageFont.FreeTypeFont
        Font for text
    color : Union[Tuple[int, int, int], str, int], optional
        Font color, by default "black"
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
