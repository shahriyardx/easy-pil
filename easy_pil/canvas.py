from typing import Tuple, Union

from PIL import Image


class Canvas:
    def __init__(
        self,
        size: Tuple[float, float],
        color: Union[Tuple[int, int, int], str, int] = None,
    ) -> None:
        self.size = size
        self.color = color

        self.image = Image.new("RGBA", size, color=color)
