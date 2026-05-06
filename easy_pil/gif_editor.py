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
        images[0].save(_bytes, "GIF", save_all=True, append_images=images[1:])

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
        images[0].save(
            fp,
            "GIF",
            save_all=True,
            append_images=images[1:],
            **kwargs,
        )
