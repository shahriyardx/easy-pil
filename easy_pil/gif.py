from io import BytesIO
from typing import List, Tuple, Union

from PIL import Image

from .editor import Editor
from .workspace import Workspace


def get_image(image: Union[Image.Image, Editor, Workspace], size: Tuple[float, float]):
    if isinstance(image, Image.Image):
        return image

    if isinstance(image, Editor):
        return image.image

    if isinstance(image, Workspace):
        return image.generate_image(size).image


class Gif:
    def __init__(
        self, size: Tuple[float, float], images: List[Union[Image.Image, Editor, Workspace]] = []
    ) -> None:
        self.frames = [
            image for image in list(map(lambda x: get_image(x, size), images)) if image
        ]
        self.size = size

    def add_frame(self, image: Union[Image.Image, Editor, Workspace]):
        self.frames.append(get_image(image, self.size))

    def save(self, filename: str, format: str = "gif", duration: float = 100):
        self.frames[0].save(
            filename,
            format=format,
            save_all=True,
            append_images=self.frames[1:],
            duration=duration,
        )

    def get(self, duration: float = 100):
        _bytes = BytesIO()
        self.frames[0].save(
            _bytes,
            format="gif",
            save_all=True,
            append_images=self.frames[1:],
            duration=duration,
        )
        _bytes.seek(0)
        return Image.open(_bytes)

    def get_bytes(self, duration: float = 100):
        _bytes = BytesIO()
        self.frames[0].save(
            _bytes,
            format="gif",
            save_all=True,
            append_images=self.frames[1:],
            duration=duration,
        )
        _bytes.seek(0)

        return _bytes
