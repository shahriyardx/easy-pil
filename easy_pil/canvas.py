from typing import Tuple, Union

from PIL import Image


class Canvas:
    """Canvas class

    :param size: Size of image, defaults to None
    :type size: Tuple[float, float], optional
    :param width: Width of image, defaults to None
    :type width: float, optional
    :param height: Height of image, defaults to None
    :type height: float, optional
    :param color: Color of image, defaults to None
    :type color: Union[Tuple[int, int, int], str, int], optional
    :raises ValueError: When either size or width and height is not a provided
    :return: None
    :rtype: None
    """
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
