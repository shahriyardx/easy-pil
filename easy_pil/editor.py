from __future__ import annotations
from .font import Font
from io import BytesIO
from .canvas import Canvas
from typing import Union, Tuple
from typing_extensions import Literal
from PIL import Image, ImageDraw, ImageFilter, ImageFont


class Editor:
    """Editor class"""

    def __init__(self, image: Union[Image.Image, str, Editor, Canvas]) -> None:
        if type(image) == str:
            self.image = Image.open(image)
        elif isinstance(image, Canvas) or isinstance(image, Editor):
            self.image = image.image
        else:
            self.image = image
        self.image = self.image.convert("RGBA")

    @property
    def image_bytes(self) -> BytesIO:
        _bytes = BytesIO()
        self.image.save(_bytes, "png")
        _bytes.seek(0)

        return _bytes

    def resize(self, size: Tuple[float, float], crop=False):
        """Resize an image to given size"""
        if not crop:
            self.image = self.image.resize(size, Image.ANTIALIAS)

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

    def rounded_corners(self, radius: int = 10, offset: int=2):
        """Make image corners rounded"""
        background = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))
        holder = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))
        mask = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            (offset, offset) + (self.image.size[0] - 2, self.image.size[1] - offset),
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

    def rotate(self, deg: float = 0, expand: bool = False):
        """Rotate image to given degree"""
        self.image = self.image.rotate(angle=deg, expand=expand)

        return self

    def blur(self, mode: Literal["box", "gussian"] = "gussian", amount: float = 1):
        """Blur image"""

        if mode == "box":
            self.image = self.image.filter(ImageFilter.BoxBlur(radius=amount))
        if mode == "gussian":
            self.image = self.image.filter(ImageFilter.GaussianBlur(radius=amount))

        return self

    def blend(
        self,
        image: Union[Image.Image, Editor, Canvas],
        alpha: float = 0.0,
        on_top: bool = False,
    ):
        """Blend image"""
        if type(image) == Editor or type(image) == Canvas:
            image = image.image

        if image.size != self.image.size:
            image = Editor(image).resize(self.image.size, crop=True).image

        if on_top:
            self.image = Image.blend(self.image, image, alpha=alpha)

        self.image = Image.blend(image, self.image, alpha=alpha)

        return self

    def paste(
        self, image: Union[Image.Image, Editor, Canvas], position: Tuple[float, float]
    ):
        """Paste image into another"""
        blank = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))

        if type(image) == Editor or type(image) == Canvas:
            image = image.image

        blank.paste(image, position)
        self.image = Image.alpha_composite(self.image, blank)

        return self

    def text(
        self,
        position: Tuple[float, float],
        text: str,
        font: Union[ImageFont.FreeTypeFont, Font] = None,
        color: Union[Tuple[int, int, int], str, int] = "black",
        align: Literal["left", "center", "right"] = "left",
    ):
        """Draw text into image"""
        if type(font) == Font:
            font = font.font

        anchors = {"left": "lt", "center": "mt", "right": "rt"}

        draw = ImageDraw.Draw(self.image)
        draw.text(position, text, color, font=font, anchor=anchors[align])

        return self

    def multicolor_text(
        self,
        position: Tuple[float, float],
        texts: list,
        space_separated: bool = True,
        align: Literal["left", "center", "right"] = "left",
    ):
        """Draw text with multiple color"""
        draw = ImageDraw.Draw(self.image)

        if align == "left":
            position = position

        if align == "right":
            total_width = 0

            for text in texts:
                total_width += text.font.getsize(text.text)[0]

            position = (position[0] - total_width, position[1])

        if align == "center":
            total_width = 0

            for text in texts:
                total_width += text.font.getsize(text.text)[0]

            position = (position[0] - (total_width / 2), position[1])

        for text in texts:
            sentence = text.text
            font = text.font
            color = text.color

            if space_separated:
                width, _ = (
                    font.getsize(sentence)[0] + font.getsize(" ")[0],
                    font.getsize(sentence)[1],
                )
            else:
                width, _ = font.getsize(sentence)

            draw.text(position, sentence, color, font=font)
            position = (position[0] + width, position[1])

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

    def rounded_bar(
        self,
        position: Tuple[float, float],
        width: Union[int, float],
        height: Union[int, float],
        percentage: float,
        fill: Union[str, int, Tuple[int, int, int]] = None,
        stroke_width: float = 1,
    ):
        draw = ImageDraw.Draw(self.image)

        start = -90
        end = (percentage * 3.6) - 90

        draw.arc(
            position + (position[0] + width, position[1] + height),
            start,
            end,
            fill,
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

    def polygon(
        self,
        cordinates: list,
        fill: Union[str, int, Tuple[int, int, int]] = None,
        outline: Union[str, int, Tuple[int, int, int]] = None,
    ):
        draw = ImageDraw.Draw(self.image)
        draw.polygon(cordinates, fill=fill, outline=outline)

        return self

    def arc(
        self,
        position: Tuple[float, float],
        width: float,
        height: float,
        start: float,
        rotation: float,
        fill: Union[str, int, Tuple[int, int, int]] = None,
        stroke_width: float = 1,
    ):
        draw = ImageDraw.Draw(self.image)

        start = start - 90
        end = rotation - 90
        draw.arc(
            position + (position[0] + width, position[1] + height),
            start,
            end,
            fill,
            width=stroke_width,
        )

        return self

    def show(self):
        """Show the image."""
        self.image.show()
    
    def save(self, fp, format=None, **params):
        """Save the image"""
        self.image.save(fp, format, **params)
