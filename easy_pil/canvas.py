from typing import Optional, Tuple

from PIL import Image

from .types.common import Color


class Canvas:
    """Canvas class

    Parameters
    ----------
    size : Tuple[int, int], optional
        Size of image, by default None
    width : int, optional
        Width of image, by default None
    height : int, optional
        Height of image, by default None
    color : Color, optional
        Color of image, by default None

    Raises
    ------
    ValueError
        When either ``size`` or ``width and height`` is not a provided
    """

    def __init__(
        self,
        size: Optional[Tuple[int, int]] = None,
        width: int = 0,
        height: int = 0,
        color: Color = 0,
    ) -> None:
        if not (size or (width and height)):
            raise ValueError("size, width, and height cannot all be None")

        elif not size:
            size = (width, height)

        self.size = size
        self.color = color

        self.image = Image.new("RGBA", size, color=color)
