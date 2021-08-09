from io import BytesIO
from typing import Union, Tuple
from PIL import Image, ImageDraw, ImageFont
from .canvas import Canvas
from .font import Font


class Editor:
    """Editor class"""

    def __init__(
        self, image: Union[Image.Image, str] = None, canvas: Canvas = None
    ) -> None:
        if image:
            if type(image) == str:
                self.image: Image.Image = Image.open(image)
            else:
                self.image: Image.Image = image

            self.image = self.image.convert("RGBA")
        else:
            if canvas:
                self.image = Image.new(
                    mode="RGBA", size=canvas.size, color=canvas.color
                )
            else:
                raise ValueError(
                    "'color' and 'size' is required to when no image is supplied"
                )

    @property
    def image_bytes(self) -> BytesIO:
        _bytes = BytesIO()
        self.image.save(_bytes, "png")
        _bytes.seek(0)

        return _bytes

    def resize(self, size: Tuple[float, float], crop=False):
        """Resize an image to given size"""
        if not crop:
            self.image = self.image.resize(size)

        else:
            width, height = self.image.size
            ideal_width, ideal_height = size

            aspect = width / float(height)
            ideal_aspect = ideal_width / float(ideal_height)

            if aspect > ideal_aspect:
                new_width = int(ideal_aspect * height)
                offset = (width - new_width) / 2
                resize = (offset, 0, width - offset, height)
            else:
                new_height = int(width / ideal_aspect)
                offset = (height - new_height) / 2
                resize = (0, offset, width, height - offset)

            self.image = self.image.crop(resize).resize(
                (ideal_width, ideal_height), Image.ANTIALIAS
            )

        return self

    def rouded_corners(self, radius: int = 10):
        """Make image corners rounded"""
        background = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))
        holder = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))

        mask = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))
        mask_draw = ImageDraw.Draw(mask)

        mask_draw.rounded_rectangle(
            (5, 5) + (self.image.size[0] - 5, self.image.size[1] - 5),
            radius=radius,
            fill="black",
        )

        holder.paste(self.image, (0, 0))
        self.image = Image.composite(holder, background, mask)

        return self

    def circle_image(self):
        """Make image circular"""
        background = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))
        holder = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))

        mask = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))
        mask_draw = ImageDraw.Draw(mask)

        mask_draw.ellipse((0, 0) + self.image.size, fill="black")

        holder.paste(self.image, (0, 0))
        self.image = Image.composite(holder, background, mask)

        return self

    def paste(self, image: Image.Image, position: Tuple[float, float]):
        """Paste image into another"""
        blank = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))

        blank.paste(image, position)

        self.image = Image.alpha_composite(self.image, blank)
        return self

    def text(
        self,
        position: Tuple[float, float],
        text: str,
        font: Union[ImageFont.FreeTypeFont, Font] = None,
        color: Union[Tuple[int, int, int], str, int] = "black",
        anchor: str = None,
    ):
        """Draw text into image"""
        if type(font) == Font:
            font = font.font

        draw = ImageDraw.Draw(self.image)
        draw.text(position, text, color, font=font, anchor=anchor)

        return self

    def rectangle(
        self,
        position: Tuple[float, float],
        width: float,
        height: float,
        fill: Union[str, int, Tuple[int, int, int]] = None,
        outline: Union[str, int, Tuple[int, int, int]] = None,
        stroke_width: float = 1,
        radius: int = 0,
    ):
        """Draw rectangle into image"""
        draw = ImageDraw.Draw(self.image)

        to_width = width + position[0]
        to_height = height + position[1]

        if radius <= 0:
            draw.rectangle(
                position + (to_width, to_height),
                fill=fill,
                outline=outline,
                width=stroke_width,
            )
        else:
            draw.rounded_rectangle(
                position + (to_width, to_height),
                radius=radius,
                fill=fill,
                outline=outline,
                width=stroke_width,
            )

        return self

    def bar(
        self,
        position: Tuple[float, float],
        max_width: Union[int, float],
        height: Union[int, float],
        percentage: int = 1,
        fill: Union[str, int, Tuple[int, int, int]] = None,
        outline: Union[str, int, Tuple[int, int, int]] = None,
        stroke_width: float = 1,
        radius: int = 0,
    ):
        """Make progerss bar"""
        draw = ImageDraw.Draw(self.image)

        ratio = max_width / 100
        to_width = ratio * percentage + position[0]

        height = height + position[1]

        if radius <= 0:
            draw.rectangle(
                position + (to_width, height),
                fill=fill,
                outline=outline,
                width=stroke_width,
            )
        else:
            draw.rounded_rectangle(
                position + (to_width, height),
                radius=radius,
                fill=fill,
                outline=outline,
                width=stroke_width,
            )

        return self

    def ellipse(
        self,
        position: Tuple[float, float],
        width: float,
        height: float,
        fill: Union[str, int, Tuple[int, int, int]] = None,
        outline: Union[str, int, Tuple[int, int, int]] = None,
        stroke_width: float = 1,
    ):
        """Make ellipse"""
        draw = ImageDraw.Draw(self.image)
        to_width = width + position[0]
        to_height = height + position[1]

        draw.ellipse(
            position + (to_width, to_height),
            outline=outline,
            fill=fill,
            width=stroke_width,
        )

        return self

    def show(self):
        """Show the image."""
        self.image.show()
