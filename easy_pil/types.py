from typing import List, Tuple, TypedDict, Union

from PIL.Image import Image
from PIL.ImageFont import FreeTypeFont
from typing_extensions import Literal

from .canvas import Canvas
from .editor import Editor
from .font import Font
from .text import Text

RGB = Union[Tuple[int, int, int], Tuple[int, int, int, int]]
Color = Union[str, int, RGB]


class ComponentKwargs(TypedDict):
    size: Tuple[float, float]
    position: Tuple[float, float]
    crop: bool
    radius: int
    offset: int
    deg: float
    expand: bool
    mode: Literal["box", "gussian"]
    amount: float
    image: Union[Image, Editor, Canvas]
    alpha: float
    on_top: bool
    text: str
    font: Union[FreeTypeFont, Font]
    align: Literal["left", "center", "right"]
    color: str
    fill: str
    space_separated: bool
    texts: List[Text]
    width: float
    height: float
    stoke_width: float
    outline: float
    max_width: float
    percent: int
    start: float
    rotation: int
