from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import List, Literal, Optional, Tuple, Union

from PIL import ImageFont
from PIL.Image import Image

from .canvas import Canvas
from .editor import Editor
from .font import Font
from .text import Text
from .types.common import Color


@dataclass
class Instruction:
    name: str
    args: list = field(default_factory=lambda: [])
    kwargs: dict = field(default_factory=lambda: {})


class AioEditor:
    def __init__(
        self, _image: Union[Image, str, BytesIO, Editor, Canvas, Path]
    ) -> None:
        self.image = _image
        self.instructions: List[Instruction] = []

    def resize(self, size: Tuple[int, int], crop=False) -> AioEditor:
        self.instructions.append(Instruction(name="resize", args=[size, crop]))
        return self

    def rounded_corners(self, radius: int = 10, offset: int = 2) -> AioEditor:
        self.instructions.append(
            Instruction(name="rounded_corners", args=[radius, offset])
        )
        return self

    def circle_image(self) -> AioEditor:
        self.instructions.append(Instruction(name="circle_image"))
        return self

    def rotate(self, deg: float = 0, expand: bool = False) -> AioEditor:
        self.instructions.append(
            Instruction(name="rotate", args=[deg, expand])
        )
        return self

    def blur(
        self, mode: Literal["box", "gaussian"] = "gaussian", amount: float = 1
    ) -> AioEditor:
        self.instructions.append(Instruction(name="blur", args=[mode, amount]))
        return self

    def blend(
        self,
        image: Union[Image, Editor, Canvas],
        alpha: float = 0.0,
        on_top: bool = False,
    ) -> AioEditor:
        self.instructions.append(
            Instruction(name="blend", args=[image, alpha, on_top])
        )
        return self

    def paste(
        self,
        image: Union[Image, Editor, Canvas],
        position: Tuple[int, int],
    ) -> AioEditor:
        self.instructions.append(
            Instruction(name="paste", args=[image, position])
        )
        return self

    def text(
        self,
        position: Tuple[float, float],
        text: str,
        font: Optional[Union[ImageFont.FreeTypeFont, Font]] = None,
        color: Color = "black",
        align: Literal["left", "center", "right"] = "left",
        stroke_width: Optional[int] = None,
        stroke_fill: Color = "black",
    ) -> AioEditor:
        self.instructions.append(
            Instruction(
                name="text",
                args=[
                    position,
                    text,
                    font,
                    color,
                    align,
                    stroke_width,
                    stroke_fill,
                ],
            )
        )
        return self

    def multi_text(
        self,
        position: Tuple[float, float],
        texts: List[Text],
        space_separated: bool = True,
        align: Literal["left", "center", "right"] = "left",
    ) -> AioEditor:
        self.instructions.append(
            Instruction(
                name="multi_text",
                args=[position, texts, space_separated, align],
            )
        )
        return self

    def rectangle(
        self,
        position: Tuple[float, float],
        width: float,
        height: float,
        fill: Optional[Color] = None,
        color: Optional[Color] = None,
        outline: Optional[Color] = None,
        stroke_width: float = 1,
        radius: int = 0,
    ) -> AioEditor:
        self.instructions.append(
            Instruction(
                name="rectangle",
                args=[
                    position,
                    width,
                    height,
                    fill,
                    color,
                    outline,
                    stroke_width,
                    radius,
                ],
            )
        )
        return self

    def bar(
        self,
        position: Tuple[float, float],
        max_width: Union[int, float],
        height: Union[int, float],
        percentage: int = 1,
        fill: Optional[Color] = None,
        color: Optional[Color] = None,
        outline: Optional[Color] = None,
        stroke_width: float = 1,
        radius: int = 0,
    ) -> AioEditor:
        self.instructions.append(
            Instruction(
                name="bar",
                args=[
                    radius,
                    position,
                    max_width,
                    height,
                    percentage,
                    fill,
                    color,
                    outline,
                    stroke_width,
                ],
            )
        )
        return self

    def rounded_bar(
        self,
        position: Tuple[float, float],
        width: Union[int, float],
        height: Union[int, float],
        percentage: float,
        fill: Optional[Color] = None,
        color: Optional[Color] = None,
        stroke_width: float = 1,
    ) -> AioEditor:
        self.instructions.append(
            Instruction(
                name="rounded_bar",
                args=[
                    position,
                    width,
                    height,
                    percentage,
                    fill,
                    color,
                    stroke_width,
                ],
            )
        )
        return self

    def ellipse(
        self,
        position: Tuple[float, float],
        width: float,
        height: float,
        fill: Optional[Color] = None,
        color: Optional[Color] = None,
        outline: Optional[Color] = None,
        stroke_width: float = 1,
    ) -> AioEditor:
        self.instructions.append(
            Instruction(
                name="ellipse",
                args=[
                    position,
                    width,
                    height,
                    fill,
                    color,
                    outline,
                    stroke_width,
                ],
            )
        )
        return self

    def polygon(
        self,
        coordinates: list,
        fill: Optional[Color] = None,
        color: Optional[Color] = None,
        outline: Optional[Color] = None,
    ) -> AioEditor:
        self.instructions.append(
            Instruction(
                name="polygon", args=[coordinates, fill, color, outline]
            )
        )
        return self

    def arc(
        self,
        position: Tuple[float, float],
        width: float,
        height: float,
        start: float,
        rotation: float,
        fill: Optional[Color] = None,
        color: Optional[Color] = None,
        stroke_width: float = 1,
    ) -> AioEditor:
        self.instructions.append(
            Instruction(
                name="arc",
                args=[
                    position,
                    width,
                    height,
                    start,
                    rotation,
                    fill,
                    color,
                    stroke_width,
                ],
            )
        )
        return self

    async def execute(self):
        editor = Editor(self.image)
        for ins in self.instructions:
            await asyncio.get_event_loop().run_in_executor(None, editor.__getattribute__(ins.name), *ins.args)

        return editor
