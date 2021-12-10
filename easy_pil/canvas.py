from typing import Tuple, Union

from PIL import Image


class Canvas:
    """Generate blank image with given size and color
        
    Arguments:
        size {Tuple[float, float]} -- size of image (default: {None})
        width {float} -- width of image (default: {None})
        height {float} -- height of image (default: {None})
        color {Union[Tuple[int, int, int], str, int]} -- color of image (default: {None})

    Returns:
        None
    """
    def __init__(
        self,
        size: Tuple[float, float]=None,
        width: float = None,
        height: float = None,
        color: Union[Tuple[int, int, int], str, int] = None,
    ) -> None:
        """Generate blank image with given size and color"""
        if not size and not width and not height:
            raise ValueError("size, width, and height cannot all be None")
        
        if width and height:
            size = (width, height)
        
        self.size = size
        self.color = color

        self.image = Image.new("RGBA", size, color=color)
