"""Module for async image editing using AioEditor."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from functools import partial
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL.Image import Image

from .canvas import Canvas
from .editor import Editor


@dataclass
class Instruction:
    """Represents a single editor instruction to be executed asynchronously."""

    name: str
    args: Sequence[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)


class AioEditor:
    """Asynchronous wrapper around Editor for non-blocking image processing."""

    def __init__(
        self,
        source: Image | str | BytesIO | Editor | Canvas | Path,
    ) -> None:
        """Initialize AioEditor with an image source."""
        self.image = source
        self.instructions: list[Instruction] = []

    def __getattr__(self, name: str) -> Callable[..., None]:
        """Dynamically create handler methods for Editor methods."""
        attr = inspect.getattr_static(Editor, name, None)
        if (
            callable(attr)
            and not isinstance(attr, property)
            and not name.startswith("_")
        ):

            def handler(*args: Any, **kwargs: Any) -> None:
                self.instructions.append(
                    Instruction(name=name, args=args, kwargs=kwargs),
                )

            return handler
        msg = f"'{name}' is not available in Editor"
        raise AttributeError(msg)

    async def execute(self) -> Editor:
        """Execute all queued instructions asynchronously and return Editor."""
        editor = Editor(self.image)
        for ins in self.instructions:
            func = partial(
                editor.__getattribute__(ins.name),
                *ins.args,
                **ins.kwargs,
            )
            await asyncio.get_running_loop().run_in_executor(None, func)

        return editor
