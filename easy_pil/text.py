from typing import Tuple, Union

from PIL import ImageFont


class Text:
    """Text class for making multicolor text
    
    Args:
        text (str): The text to be displayed
        font (ImageFont.FreeTypeFont): The font to be used
        color (Union[Tuple[int, int, int], str, int], optional): The color of the text. Defaults to "black".

    Returns:
        None
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
