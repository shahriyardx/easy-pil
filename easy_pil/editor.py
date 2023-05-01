from __future__ import annotations

from io import BytesIO
from typing import List, Optional, Tuple, Union

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from typing_extensions import Literal

from .canvas import Canvas
from .font import Font
from .text import Text
from .types.common import Color


class Editor:
    """Editor class. It does all the editing operations.

    Parameters
    ----------
    image : Union[Image.Image, str, Editor, Canvas]
        Image or Canvas to edit.
    """

    def __init__(
        self, image: Union[Image.Image, str, BytesIO, Editor, Canvas]
    ) -> None:
        self.image = None

        if isinstance(image, str) or isinstance(image, BytesIO):
            self.image = Image.open(image).convert("RGBA")
        elif isinstance(image, Canvas) or isinstance(image, Editor):
            self.image = image.image.convert("RGBA")
        else:
            self.image = image.convert("RGBA")

    @property
    def image_bytes(self) -> BytesIO:
        """Return image bytes

        Returns
        -------
        BytesIO
            Bytes from the image of Editor
        """
        _bytes = BytesIO()
        self.image.save(_bytes, "png")

        _bytes.seek(0)
        return _bytes

    def resize(self, size: Tuple[float, float], crop=False) -> Editor:
        """Resize image

        Parameters
        ----------
        size : Tuple[float, float]
            New Size of image
        crop : bool, optional
            Crop the image to bypass distortion, by default False
        """
        if not crop:
            self.image = self.image.resize(size, Image.LANCZOS)

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
                (ideal_width, ideal_height), Image.LANCZOS
            )

        return self

    def rounded_corners(self, radius: int = 10, offset: int = 2) -> Editor:
        """Make image rounded corners

        Parameters
        ----------
        radius : int, optional
            Radius of roundness, by default 10
        offset : int, optional
            Offset pixel while making rounded, by default 2
        """
        background = Image.new(
            "RGBA", size=self.image.size, color=(255, 255, 255, 0)
        )
        holder = Image.new(
            "RGBA", size=self.image.size, color=(255, 255, 255, 0)
        )
        mask = Image.new(
            "RGBA", size=self.image.size, color=(255, 255, 255, 0)
        )
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            (offset, offset)
            + (self.image.size[0] - offset, self.image.size[1] - offset),
            radius=radius,
            fill="black",
        )
        holder.paste(self.image, (0, 0))
        self.image = Image.composite(holder, background, mask)

        return self

    def circle_image(self) -> Editor:
        """Make image circle"""
        background = Image.new(
            "RGBA", size=self.image.size, color=(255, 255, 255, 0)
        )
        holder = Image.new(
            "RGBA", size=self.image.size, color=(255, 255, 255, 0)
        )
        mask = Image.new(
            "RGBA", size=self.image.size, color=(255, 255, 255, 0)
        )
        mask_draw = ImageDraw.Draw(mask)
        ellipse_size = tuple(i - 1 for i in self.image.size)
        mask_draw.ellipse((0, 0) + ellipse_size, fill="black")
        holder.paste(self.image, (0, 0))
        self.image = Image.composite(holder, background, mask)

        return self

    def rotate(self, deg: float = 0, expand: bool = False) -> Editor:
        """Rotate image

        Parameters
        ----------
        deg : float, optional
            Degress to rotate, by default 0
        expand : bool, optional
            Expand while rotating, by default False
        """
        self.image = self.image.rotate(angle=deg, expand=expand)
        return self

    def blur(
        self, mode: Literal["box", "gussian"] = "gussian", amount: float = 1
    ) -> Editor:
        """Blur image

        Parameters
        ----------
        mode : Literal["box", "gussian"], optional
            Blur mode, by default "gussian"
        amount : float, optional
            Amount of blur, by default 1
        """
        if mode == "box":
            self.image = self.image.filter(ImageFilter.BoxBlur(radius=amount))
        if mode == "gussian":
            self.image = self.image.filter(
                ImageFilter.GaussianBlur(radius=amount)
            )

        return self

    def blend(
        self,
        image: Union[Image.Image, Editor, Canvas],
        alpha: float = 0.0,
        on_top: bool = False,
    ) -> Editor:
        """Blend image into editor image

        Parameters
        ----------
        image : Union[Image.Image, Editor, Canvas]
            Image to blend
        alpha : float, optional
            Alpha amount, by default 0.0
        on_top : bool, optional
            Places image on top, by default False
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
        self,
        image: Union[Image.Image, Editor, Canvas],
        position: Tuple[float, float],
    ) -> Editor:
        """Paste image into editor

        Parameters
        ----------
        image : Union[Image.Image, Editor, Canvas]
            Image to paste
        position : Tuple[float, float]
            Position to paste
        """
        blank = Image.new(
            "RGBA", size=self.image.size, color=(255, 255, 255, 0)
        )

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
        color: Color = "black",
        align: Literal["left", "center", "right"] = "left",
        stroke: Optional[Union[int, Tuple[int], Tuple[int, str]]] = None,
    ) -> Editor:
        """Draw text into image

        Parameters
        ----------
        position : Tuple[float, float]
            Position to draw text
        text : str
            Text to draw
        font : Union[ImageFont.FreeTypeFont, Font], optional
            Font used for text, by default None
        color : Color, optional
            Color of the font, by default "black"
        align : Literal["left", "center", "right"], optional
            Align text, by default "left"
        stroke : Union[int, Tuple[int], Tuple[int, str]], optional
            Whether there should be any stroke. Defaults to
            None. If only one parameter is passed, the
            default color is black.
        """
        if isinstance(font, Font):
            font = font.font

        anchors = {"left": "lt", "center": "mt", "right": "rt"}

        draw = ImageDraw.Draw(self.image)

        if stroke:
            if isinstance(stroke, int):
                draw.text(position, text, color, font=font, anchor=anchors[align],
                          stroke_width=stroke, stroke_fill="black")
            elif len(stroke) > 1:
                draw.text(position, text, color, font=font, anchor=anchors[align],
                          stroke_width=stroke[0], stroke_fill=stroke[1])
            else:
                draw.text(position, text, color, font=font, anchor=anchors[align],
                          stroke_width=stroke[0], stroke_fill="black")
        else:
            draw.text(position, text, color, font=font, anchor=anchors[align])

        return self

    def multi_text(
        self,
        position: Tuple[float, float],
        texts: List[Text],
        space_separated: bool = True,
        align: Literal["left", "center", "right"] = "left",
    ) -> Editor:
        """Draw multicolor text

        Parameters
        ----------
        position : Tuple[float, float]
            Position to draw text
        texts : List[Text]
            List of texts
        space_separated : bool, optional
            Separate texts with space, by default True
        align : Literal["left", "center", "right"], optional
            Align texts, by default "left"
        """
        draw = ImageDraw.Draw(self.image)

        if align == "left":
            position = position

        if align == "right":
            total_width = 0

            for text in texts:
                total_width += text.font.getlength(text.text)

            position = (position[0] - total_width, position[1])

        if align == "center":
            total_width = 0

            for text in texts:
                total_width += text.font.getlength(text.text)

            position = (position[0] - (total_width / 2), position[1])

        for text in texts:
            sentence = text.text
            font = text.font
            color = text.color

            if space_separated:
                width = font.getlength(sentence + " ")
            else:
                width = font.getlength(sentence)

            draw.text(position, sentence, color, font=font, anchor="lm")
            position = (position[0] + width, position[1])

        return self

    def rectangle(
        self,
        position: Tuple[float, float],
        width: float,
        height: float,
        fill: Color = None,
        color: Color = None,
        outline: Color = None,
        stroke_width: float = 1,
        radius: int = 0,
    ) -> Editor:
        """Draw rectangle into image

        Parameters
        ----------
        position : Tuple[float, float]
            Position to draw recangle
        width : float
            Width of rectangle
        height : float
            Height of rectangle
        fill : Color, optional
            Fill color, by default None
        color : Color, optional
            Alias of fill, by default None
        outline : Color, optional
            Outline color, by default None
        stroke_width : float, optional
            Stroke width, by default 1
        radius : int, optional
            Radius of rectangle, by default 0
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
        fill: Color = None,
        color: Color = None,
        outline: Color = None,
        stroke_width: float = 1,
        radius: int = 0,
    ) -> Editor:
        """Draw a progress bar

        Parameters
        ----------
        position : Tuple[float, float]
            Position to draw bar
        max_width : Union[int, float]
            Max width of the bar
        height : Union[int, float]
            Height of the bar
        percentage : int, optional
            Percebtage to fill of the bar, by default 1
        fill : Color, optional
            Fill color, by default None
        color : Color, optional
            Alias of fill, by default None
        outline : Color, optional
            Outline color, by default None
        stroke_width : float, optional
            Stroke width, by default 1
        radius : int, optional
            Radius of the bar, by default 0
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
        fill: Color = None,
        color: Color = None,
        stroke_width: float = 1,
    ) -> Editor:
        """Draw a rounded bar

        Parameters
        ----------
        position : Tuple[float, float]
            Position to draw rounded bar
        width : Union[int, float]
            Width of the bar
        height : Union[int, float]
            Height of the bar
        percentage : float
            Percentage to fill
        fill : Color, optional
            Fill color, by default None
        color : Color, optional
            Alias of color, by default None
        stroke_width : float, optional
            Stroke width, by default 1
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
        fill: Color = None,
        color: Color = None,
        outline: Color = None,
        stroke_width: float = 1,
    ) -> Editor:
        """Draw an ellipse

        Parameters
        ----------
        position : Tuple[float, float]
            Position to draw ellipse
        width : float
            Width of ellipse
        height : float
            Height of ellipse
        fill : Color, optional
            Fill color, by default None
        color : Color, optional
            Alias of fill, by default None
        outline : Color, optional
            Outline color, by default None
        stroke_width : float, optional
            Stroke width, by default 1
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
        fill: Color = None,
        color: Color = None,
        outline: Color = None,
    ) -> Editor:
        """Draw a polygon

        Parameters
        ----------
        cordinates : list
            Cordinates to draw
        fill : Color, optional
            Fill color, by default None
        color : Color, optional
            Alias of fill, by default None
        outline : Color, optional
            Outline color, by default None
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
        fill: Color = None,
        color: Color = None,
        stroke_width: float = 1,
    ) -> Editor:
        """Draw arc

        Parameters
        ----------
        position : Tuple[float, float]
            Position to draw arc
        width : float
            Width or arc
        height : float
            Height of arch
        start : float
            Start position of arch
        rotation : float
            Rotation in degre
        fill : Color, optional
            Fill color, by default None
        color : Color, optional
            Alias of fill, by default None
        stroke_width : float, optional
            Stroke width, by default 1
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

    def save(self, fp, format: str = None, **params):
        """Save the image

        Parameters
        ----------
        fp : str
            File path
        format : str, optional
            File format, by default None
        """
        self.image.save(fp, format, **params)
