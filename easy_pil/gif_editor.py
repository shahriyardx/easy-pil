"""GIF image editing support."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image as PilImage
from PIL import ImageSequence
from PIL.GifImagePlugin import GifImageFile
from PIL.Image import Image

from .editor import Editor


class GifEditor:
    """
    Editor for GIF images, applying operations lazily across all frames.

    Operations are not applied eagerly. Instead every call to an ``Editor``
    method is queued and only replayed against one decoded frame at a time when
    the GIF is rendered (``save`` / ``image_bytes``). This keeps memory usage
    bounded to a single decoded frame rather than retaining every frame as a
    full RGBA image for the object's lifetime.
    """

    def __init__(self, image: str | BytesIO | Path | GifImageFile) -> None:
        """Initialize GifEditor with a GIF image source."""
        if isinstance(image, (str, BytesIO, Path)):
            self.image = PilImage.open(image)
        elif isinstance(image, GifImageFile):
            self.image = image
        else:
            msg = (
                "image must be a str, BytesIO, Path or GifImageFile, "
                f"got {type(image).__name__}"
            )
            raise TypeError(msg)

        # Capture animation metadata before iterating/seeking frames, since
        # seeking can mutate what ``self.image.info`` holds.
        self._info: dict[Any, Any] = dict(self.image.info)
        self._n_frames: int = getattr(self.image, "n_frames", 1)
        self.size: tuple[int, int] = self.image.size
        # Queue of (method_name, args, kwargs) replayed per frame at render time.
        self._ops: list[tuple[str, tuple, dict]] = []

    def __enter__(self) -> GifEditor:
        """Context manager entry."""
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit — close source and clear queue."""
        self.close()

    def close(self) -> None:
        """Close the source image and drop the queued operations."""
        self.image.close()
        self._ops.clear()

    def __getattr__(self, name: str) -> Callable[..., None]:
        """
        Queue an Editor method call to be applied to every frame at render time.

        Only public ``Editor`` methods are intercepted; anything else (dunders,
        private names, unknown attributes) raises ``AttributeError`` so that
        real attribute access is not swallowed.
        """
        if name.startswith("_") or not hasattr(Editor, name):
            msg = f"'{type(self).__name__}' object has no attribute '{name}'"
            raise AttributeError(msg)

        def wrapper(*args: object, **kwargs: object) -> None:
            self._ops.append((name, args, kwargs))

        return wrapper

    def _render_frames(self) -> Iterator[Image]:
        """
        Yield processed frames one at a time.

        Each source frame is decoded into a single ``Editor``, the queued
        operations are replayed against it, and its image is yielded. Only one
        decoded frame is alive at a time during iteration.
        """
        for frame in ImageSequence.Iterator(self.image):
            ed = Editor(frame)
            for name, args, kwargs in self._ops:
                getattr(ed, name)(*args, **kwargs)
            yield ed.image

    def _save_kwargs(self) -> dict[str, Any]:
        """
        Build animation metadata kwargs for saving.

        Returns
        -------
        dict[str, Any]
            Save arguments preserving duration, loop and disposal. Keys that
            are unavailable in the source image info are omitted.

        """
        kwargs: dict[str, Any] = {"disposal": 2}

        duration = self._info.get("duration")
        if duration is not None:
            kwargs["duration"] = duration

        loop = self._info.get("loop")
        if loop is not None:
            kwargs["loop"] = loop

        return kwargs

    @property
    def image_bytes(self) -> BytesIO:
        """
        Return image bytes.

        Returns
        -------
        BytesIO
            Bytes from the image of Editor

        """
        _bytes = BytesIO()
        self.save(_bytes)
        _bytes.seek(0)
        return _bytes

    def save(self, fp: str | Path | BytesIO, **kwargs: Any) -> None:
        """
        Save the image.

        Parameters
        ----------
        fp : str | Path | BytesIO
            File path or buffer
        **kwargs
            Additional arguments passed to PIL save

        """
        # Rendering is lazy, but Pillow's ``save_all``/``append_images`` needs
        # every output frame at once, so save-time still materializes the list
        # of processed frames. True streaming GIF writing isn't available.
        frames = list(self._render_frames())
        save_kwargs = {**self._save_kwargs(), **kwargs}
        frames[0].save(
            fp,
            "GIF",
            save_all=True,
            append_images=frames[1:],
            **save_kwargs,
        )
