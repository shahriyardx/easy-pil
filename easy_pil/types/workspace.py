from io import BytesIO
from pathlib import Path
from typing import List, Tuple, Union

try:
    from typing import Literal, NotRequired, TypedDict
except ImportError:
    from typing_extensions import TypedDict, NotRequired, Literal

from PIL.Image import Image
from PIL.ImageFont import FreeTypeFont

from ..canvas import Canvas
from ..editor import Editor
from ..font import Font
from ..text import Text


class ComponentKwargs(TypedDict):
    size: NotRequired[Tuple[float, float]]
    position: NotRequired[Tuple[float, float]]
    crop: NotRequired[bool]
    radius: NotRequired[int]
    offset: NotRequired[int]
    deg: NotRequired[float]
    expand: NotRequired[bool]
    mode: NotRequired[Literal["box", "gaussian"]]
    amount: NotRequired[float]
    image: NotRequired[Union[Image, Editor, Canvas, BytesIO, Path, bytes]]
    alpha: NotRequired[float]
    on_top: NotRequired[bool]
    text: NotRequired[str]
    font: NotRequired[Union[FreeTypeFont, Font]]
    align: NotRequired[Literal["left", "center", "right"]]
    color: NotRequired[
        Union[int, str, Tuple[int, int, int], Tuple[int, int, int, int]]
    ]
    fill: NotRequired[
        Union[int, str, Tuple[int, int, int], Tuple[int, int, int, int]]
    ]
    space_separated: NotRequired[bool]
    texts: NotRequired[List[Text]]
    width: NotRequired[float]
    height: NotRequired[float]
    stoke_width: NotRequired[float]
    outline: NotRequired[float]
    max_width: NotRequired[float]
    percent: NotRequired[int]
    start: NotRequired[float]
    rotation: NotRequired[int]
