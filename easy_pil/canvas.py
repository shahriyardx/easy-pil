"""Canvas module for creating blank images."""

from PIL import Image

from .gradient import Gradient

Color = int | str | tuple[int, int, int] | tuple[int, int, int, int]


class Canvas:
    """
    Canvas class.

    Parameters
    ----------
    size : Tuple[int, int], optional
        Size of image, by default None
    width : int, optional
        Width of image, by default None
    height : int, optional
        Height of image, by default None
    color : Color | Gradient, optional
        Color or Gradient of image, by default None

    Raises
    ------
    ValueError
        When either ``size`` or ``width and height`` is not a provided

    """

    def __init__(
        self,
        size: tuple[int, int] | None = None,
        width: int = 0,
        height: int = 0,
        color: Color | Gradient = 0,
    ) -> None:
        """Initialize Canvas."""
        if size is None and not (width > 0 and height > 0):
            msg = "Provide either size or both width and height"
            raise ValueError(msg)

        if not size:
            size = (width, height)

        self.size = size
        self.color = color

        if isinstance(color, Gradient):
            self.image = color.render(*size)
        else:
            self.image = Image.new("RGBA", size, color=color)
