from __future__ import annotations

from io import BytesIO
from typing import List, Tuple, Union

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from typing_extensions import Literal

from .canvas import Canvas
from .font import Font
from .text import Text


class Editor:
    def __init__(self, image: Union[Image.Image, str, Editor, Canvas]) -> None:
        """Editor class. It does all the editing operations.

        :param image: Image or Canvas to edit.
        :type image: Union[Image.Image, str, Editor, Canvas]
        """
        if isinstance(image, str):
            self.image = Image.open(image)
        elif isinstance(image, Canvas) or isinstance(image, Editor):
            self.image = image.image
        else:
            self.image = image

        self.image = self.image.convert("RGBA")

    @property
    def image_bytes(self) -> BytesIO:
        """Return image bytes

        :return: Bytes from the image of Editor
        :rtype: BytesIO
        """
        _bytes = BytesIO()
        self.image.save(_bytes, "png")
        _bytes.seek(0)

        return _bytes

    def resize(self, size: Tuple[float, float], crop=False) -> Editor:
        """Resize image

        :param size: Size to resize to
        :type size: Tuple[float, float]
        :param crop: Crop the image, defaults to False
        :type crop: bool, optional
        """
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

    def rounded_corners(self, radius: int = 10, offset: int = 2) -> Editor:
        """Make image rounded corners

        :param radius: Radius of roundness, defaults to 10
        :type radius: int, optional
        :param offset: Offset pixel while making rounded, defaults to 2
        :type offset: int, optional
        """
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

    def circle_image(self) -> Editor:
        """Make image circle"""
        background = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))
        holder = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))
        mask = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0) + self.image.size, fill="black")
        holder.paste(self.image, (0, 0))
        self.image = Image.composite(holder, background, mask)

        return self

    def rotate(self, deg: float = 0, expand: bool = False) -> Editor:
        """Rotate image

        :param deg: Degress to rotate, defaults to 0
        :type deg: float, optional
        :param expand: Expand while rotating, defaults to False
        :type expand: bool, optional
        """
        self.image = self.image.rotate(angle=deg, expand=expand)

        return self

    def blur(self, mode: Literal["box", "gussian"] = "gussian", amount: float = 1) -> Editor:
        """Blur image

        :param mode: Blur mode, defaults to "gussian"
        :type mode: Literal[, optional
        :param amount: Amount of blur, defaults to 1
        :type amount: float, optional
        """
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
    ) -> Editor:
        """Blend image into editor image

        :param image: Image to blend
        :type image: Union[Image.Image, Editor, Canvas]
        :param alpha: Alpha amount, defaults to 0.0
        :type alpha: float, optional
        :param on_top: Places image on top, defaults to False
        :type on_top: bool, optional
        """
        if isinstance(image, Editor) or isinstance(image, Canvas):
            image = image.image

        if image.size != self.image.size:
            image = Editor(image).resize(self.image.size, crop=True).image

        if on_top:
            self.image = Image.blend(self.image, image, alpha=alpha)
        else:
            self.image = Image.blend(image, self.image, alpha=alpha)

        return self

    def paste(
        self, image: Union[Image.Image, Editor, Canvas], position: Tuple[float, float]
    ) -> Editor:
        """Paste image

        :param image: Image to paste
        :type image: Union[Image.Image, Editor, Canvas]
        :param position: Position to paste
        :type position: Tuple[float, float]
        """
        blank = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))

        if isinstance(image, Editor) or isinstance(image, Canvas):
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
    ) -> Editor:
        """Draw text into image

        :param position: Position to draw text
        :type position: Tuple[float, float]
        :param text: Text to draw
        :type text: str
        :param font: Font used for text, defaults to None
        :type font: Union[ImageFont.FreeTypeFont, Font], optional
        :param color: Color of the font, defaults to "black"
        :type color: Union[Tuple[int, int, int], str, int], optional
        :param align: Align text, defaults to "left"
        :type align: Literal["left", "center", "right"], optional
        """
        if isinstance(font, Font):
            font = font.font

        anchors = {"left": "lt", "center": "mt", "right": "rt"}

        draw = ImageDraw.Draw(self.image)
        draw.text(position, text, color, font=font, anchor=anchors[align])

        return self

    def multicolor_text(
        self,
        position: Tuple[float, float],
        texts: List[Text],
        space_separated: bool = True,
        align: Literal["left", "center", "right"] = "left",
    ) -> Editor:
        """Draw multicolor text

        :param position: Position to draw text
        :type position: Tuple[float, float]
        :param texts: List of texts
        :type texts: List[Text]
        :param space_separated: Separate texts with space, defaults to True
        :type space_separated: bool, optional
        :param align: Align texts, defaults to "left"
        :type align: Literal["left", "center", "right"], optional
        """
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
        color: Union[str, int, Tuple[int, int, int]] = None,
        outline: Union[str, int, Tuple[int, int, int]] = None,
        stroke_width: float = 1,
        radius: int = 0,
    ) -> Editor:
        """Draw rectangle into image

        :param position: Position to draw recangle
        :type position: Tuple[float, float]
        :param width: Width of rectangle
        :type width: float
        :param height: Height of rectangle
        :type height: float
        :param fill: Fill color, defaults to None
        :type fill: Union[str, int, Tuple[int, int, int]], optional
        :param color: Alias of fill, defaults to None
        :type color: Union[str, int, Tuple[int, int, int]], optional
        :param outline: Outline color, defaults to None
        :type outline: Union[str, int, Tuple[int, int, int]], optional
        :param stroke_width: Stroke width, defaults to 1
        :type stroke_width: float, optional
        :param radius: Radius of rectangle, defaults to 0
        :type radius: int, optional
        """
        draw = ImageDraw.Draw(self.image)

        to_width = width + position[0]
        to_height = height + position[1]

        if color:
            fill = color

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
        color: Union[str, int, Tuple[int, int, int]] = None,
        outline: Union[str, int, Tuple[int, int, int]] = None,
        stroke_width: float = 1,
        radius: int = 0,
    ) -> Editor:
        """Draw a progress bar

        :param position: Position to draw bar
        :type position: Tuple[float, float]
        :param max_width: Max width of the bar
        :type max_width: Union[int, float]
        :param height: Height of the bar
        :type height: Union[int, float]
        :param percentage: Percebtage to fill of the bar, defaults to 1
        :type percentage: int, optional
        :param fill: Fill color, defaults to None
        :type fill: Union[str, int, Tuple[int, int, int]], optional
        :param color: Alias of fill, defaults to None
        :type color: Union[str, int, Tuple[int, int, int]], optional
        :param outline: Outline color, defaults to None
        :type outline: Union[str, int, Tuple[int, int, int]], optional
        :param stroke_width: Stroke width, defaults to 1
        :type stroke_width: float, optional
        :param radius: Radius of the bar, defaults to 0
        :type radius: int, optional
        """
        draw = ImageDraw.Draw(self.image)

        if color:
            fill = color

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
        color: Union[str, int, Tuple[int, int, int]] = None,
        stroke_width: float = 1,
    ) -> Editor:
        """Draw a rounded bar

        :param position: Position to draw rounded bar
        :type position: Tuple[float, float]
        :param width: Width of the bar
        :type width: Union[int, float]
        :param height: Height of the bar
        :type height: Union[int, float]
        :param percentage: Percentage to fill
        :type percentage: float
        :param fill: Fill color, defaults to None
        :type fill: Union[str, int, Tuple[int, int, int]], optional
        :param color: Alias of color, defaults to None
        :type color: Union[str, int, Tuple[int, int, int]], optional
        :param stroke_width: Stroke width, defaults to 1
        :type stroke_width: float, optional
        """
        draw = ImageDraw.Draw(self.image)

        if color:
            fill = color

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
        color: Union[str, int, Tuple[int, int, int]] = None,
        outline: Union[str, int, Tuple[int, int, int]] = None,
        stroke_width: float = 1,
    ) -> Editor:
        """Draw an ellipse

        :param position: Position to draw ellipse
        :type position: Tuple[float, float]
        :param width: Width of ellipse
        :type width: float
        :param height: Height of ellipse
        :type height: float
        :param fill: Fill color, defaults to None
        :type fill: Union[str, int, Tuple[int, int, int]], optional
        :param color: Alias of fill, defaults to None
        :type color: Union[str, int, Tuple[int, int, int]], optional
        :param outline: Outline color, defaults to None
        :type outline: Union[str, int, Tuple[int, int, int]], optional
        :param stroke_width: Stroke width, defaults to 1
        :type stroke_width: float, optional
        """
        draw = ImageDraw.Draw(self.image)
        to_width = width + position[0]
        to_height = height + position[1]

        if color:
            fill = color

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
        color: Union[str, int, Tuple[int, int, int]] = None,
        outline: Union[str, int, Tuple[int, int, int]] = None,
    ) -> Editor:
        """Draw a polygon

        :param cordinates: Cordinates to draw
        :type cordinates: list
        :param fill: Fill color, defaults to None
        :type fill: Union[str, int, Tuple[int, int, int]], optional
        :param color: Alias of fill, defaults to None
        :type color: Union[str, int, Tuple[int, int, int]], optional
        :param outline: Outline color, defaults to None
        :type outline: Union[str, int, Tuple[int, int, int]], optional
        """
        if color:
            fill = color

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
        color: Union[str, int, Tuple[int, int, int]] = None,
        stroke_width: float = 1,
    ) -> Editor:
        """Draw arc

        :param position: Position to draw arc
        :type position: Tuple[float, float]
        :param width: Width or arc
        :type width: float
        :param height: Height of arch
        :type height: float
        :param start: Start position of arch
        :type start: float
        :param rotation: Rotation in degre
        :type rotation: float
        :param fill: Fill color, defaults to None
        :type fill: Union[str, int, Tuple[int, int, int]], optional
        :param color: Alias of fill, defaults to None
        :type color: Union[str, int, Tuple[int, int, int]], optional
        :param stroke_width: Stroke width, defaults to 1
        :type stroke_width: float, optional
        """
        draw = ImageDraw.Draw(self.image)

        start = start - 90
        end = rotation - 90

        if color:
            fill = color

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

    def save(self, fp, format:str=None, **params):
        """Save the image

        :param fp: File path
        :type fp: str
        :param format: File format, defaults to None
        :type format: str, optional
        """
        self.image.save(fp, format, **params)
