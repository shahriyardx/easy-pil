from typing import Tuple, Union

from PIL import Image


class Canvas:
    def __init__(
        self,
        size: Tuple[float, float]=None,
        width: float = None,
        height: float = None,
        color: Union[Tuple[int, int, int], str, int] = None,
    ) -> None:
        if not size and not width and not height:
            raise ValueError("size, width, and height cannot all be None")
        
        if width and height:
            size = (width, height)
        
        self.size = size
        self.color = color

        self.image = Image.new("RGBA", size, color=color)
