"""GIF image editing support."""

from __future__ import annotations

from collections.abc import Callable
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image as PilImage
from PIL import ImageSequence
from PIL.GifImagePlugin import GifImageFile

from .editor import Editor


class GifEditor:
    """Editor for GIF images, applying operations across all frames."""

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
        self.original_frames = ImageSequence.Iterator(self.image)
        self.frames: list[Editor] = [Editor(x) for x in self.original_frames]
        self.size: tuple[int, int] = self.image.size

    def __enter__(self) -> GifEditor:
        """Context manager entry."""
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit — close frames and source."""
        self.close()

    def close(self) -> None:
        """Close all frame editors and source image."""
        for frame in self.frames:
            frame.close()
        self.image.close()
        self.frames.clear()

    def __getattr__(self, name: str) -> Callable:
        """Apply method calls to all frames dynamically."""

        def wrapper(*args: object, **kwargs: object) -> None:
            for frame in self.frames:
                getattr(frame, name)(*args, **kwargs)

        return wrapper

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
        images = [e.image for e in self.frames]
        images[0].save(
            _bytes,
            "GIF",
            save_all=True,
            append_images=images[1:],
            **self._save_kwargs(),
        )

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
        images = [e.image for e in self.frames]
        save_kwargs = {**self._save_kwargs(), **kwargs}
        images[0].save(
            fp,
            "GIF",
            save_all=True,
            append_images=images[1:],
            **save_kwargs,
        )
