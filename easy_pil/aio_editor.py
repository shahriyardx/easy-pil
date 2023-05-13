from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from functools import partial
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Sequence, Union

from PIL.Image import Image

from .canvas import Canvas
from .editor import Editor


@dataclass
class Instruction:
    name: str
    args: Sequence = field(default_factory=lambda: [])
    kwargs: Dict[str, Any] = field(default_factory=lambda: {})


class AioEditor:
    def __init__(
        self, _image: Union[Image, str, BytesIO, Editor, Canvas, Path]
    ) -> None:
        self.image = _image
        self.instructions: List[Instruction] = []

    def __getattr__(self, name):
        if hasattr(Editor, name):

            def handler(*args, **kwargs):
                self.instructions.append(
                    Instruction(name=name, args=args, kwargs=kwargs)
                )

            return handler
        raise AttributeError(f"'{name}' is not available in Editor")

    async def execute(self):
        editor = Editor(self.image)
        for ins in self.instructions:
            func = partial(
                editor.__getattribute__(ins.name), *ins.args, **ins.kwargs
            )
            await asyncio.get_event_loop().run_in_executor(None, func)

        return editor
