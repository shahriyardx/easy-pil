from __future__ import annotations

from io import BytesIO
from typing import List, Tuple, Union

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from typing_extensions import Literal

from .canvas import Canvas
from .font import Font
from .text import Text


class Editor:
    """Editor to edit and manipulate images"""

    def __init__(self, image: Union[Image.Image, str, Editor, Canvas]) -> None:
        if isinstance(image, str):
            self.image = Image.open(image)
        elif isinstance(image, Canvas) or isinstance(image, Editor):
            self.image = image.image
        else:
            self.image = image

        self.image = self.image.convert("RGBA")

    @property
    def image_bytes(self) -> BytesIO:
        """Return image as bytes
        
        Returns:
            BytesIO: Image as bytes
        """
        _bytes = BytesIO()
        self.image.save(_bytes, "png")
        _bytes.seek(0)

        return _bytes

    def resize(self, size: Tuple[float, float], crop=False) -> Editor:
        """Resize an image to given size
        
        Args:
            size (Tuple[float, float]): Size of the image
            crop (bool, optional): Crop image to given size. Defaults to False.
        
        Returns:
            Editor: Editor object
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
        """Add rounded corners to image
        
        Args:
            radius (int, optional): Radius of the corners. Defaults to 10.
            offset (int, optional): Offset of the corners. Defaults to 2.
        
        Returns:
            Editor: Editor object
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
        """Make image circular
        
        Returns:
            Editor: Editor object
        """
        background = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))
        holder = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))
        mask = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0) + self.image.size, fill="black")
        holder.paste(self.image, (0, 0))
        self.image = Image.composite(holder, background, mask)

        return self

    def rotate(self, deg: float = 0, expand: bool = False):
        """Rotate image to given degree
        
        Args:
            deg (float, optional): Degree to rotate. Defaults to 0.
            expand (bool, optional): Expand image to fit rotated image. Defaults to False.

        Returns:
            Editor: Editor object
        """
        self.image = self.image.rotate(angle=deg, expand=expand)

        return self

    def blur(self, mode: Literal["box", "gussian"] = "gussian", amount: float = 1) -> Editor:
        """Blur image
        
        Args:
            mode (Literal['box', 'gussian'], optional): Blur mode. Defaults to 'gussian'.
            amount (float, optional): Amount of blur. Defaults to 1.
        
        Returns:
            Editor: Editor object
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
        """Blend image into another one
        
        Args:
            image (Union[Image.Image, Editor, Canvas]): Image to blend into
            alpha (float, optional): Alpha of the image. Defaults to 0.0.
            on_top (bool, optional): Blend image on top of another image. Defaults to False.
        
        Returns:
            Editor: Editor object
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
        """Paste image into another
        
        Args:
            image (Union[Image.Image, Editor, Canvas]): Image to paste
            position (Tuple[float, float]): Position to paste image
        
        Returns:
            Editor: Editor object
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
        
        Args:
            position (Tuple[float, float]): Position to draw text
            text (str): Text to draw
            font (Union[ImageFont.FreeTypeFont, Font], optional): Font to use. Defaults to None.
            color (Union[Tuple[int, int, int], str, int], optional): Color of the text. Defaults to "black".
            align (Literal['left', 'center', 'right'], optional): Alignment of the text. Defaults to "left".
        
        Returns:
            Editor: Editor object
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
        """Draw text with multiple color
        
        Args:
            position (Tuple[float, float]): Position to draw text
            texts (List[Text]): Texts to draw
            space_separated (bool, optional): Separate text with space. Defaults to True.
            align (Literal['left', 'center', 'right'], optional): Alignment of the text. Defaults to "left".
        
        Returns:
            Editor: Editor object
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
        
        Args: 
            position (Tuple[float, float]): Position to draw rectangle
            width (float): Width of the rectangle
            height (float): Height of the rectangle
            fill (Union[str, int, Tuple[int, int, int]], optional): Fill color of the rectangle. Defaults to None.
            color (Union[str, int, Tuple[int, int, int]], optional): Alias of fill.
            outline (Union[str, int, Tuple[int, int, int]], optional): Outline color of the rectangle. Defaults to None.
            stroke_width (float, optional): Width of the outline. Defaults to 1.
            radius (int, optional): Radius of the rectangle. Defaults to 0.
        
        Returns:
            Editor: Editor object
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
        """Make progerss bar
        
        Args:
            position (Tuple[float, float]): Position to draw bar
            max_width (Union[int, float]): Max width of the bar
            height (Union[int, float]): Height of the bar
            percentage (int, optional): Percentage of the bar. Defaults to 1.
            fill (Union[str, int, Tuple[int, int, int]], optional): Fill color of the bar. Defaults to None.
            color (Union[str, int, Tuple[int, int, int]], optional): Alias of fill.
            outline (Union[str, int, Tuple[int, int, int]], optional): Outline color of the bar. Defaults to None.
            stroke_width (float, optional): Width of the outline. Defaults to 1.
            radius (int, optional): Radius of the bar. Defaults to 0.
        
        Returns:
            Editor: Editor object
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
        """Make rounded progress bar
        
        Args:
            position (Tuple[float, float]): Position to draw bar
            width (Union[int, float]): Width of the bar
            height (Union[int, float]): Height of the bar
            percentage (float): Percentage of the bar
            fill (Union[str, int, Tuple[int, int, int]], optional): Fill color of the bar. Defaults to None.
            color (Union[str, int, Tuple[int, int, int]], optional): Alias of fill.
            stroke_width (float, optional): Width of the outline. Defaults to 1.
        
        Returns:
            Editor: Editor object
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
        """Draw ellipse into image
        
        Args:
            position (Tuple[float, float]): Position to draw ellipse
            width (float): Width of the ellipse
            height (float): Height of the ellipse
            fill (Union[str, int, Tuple[int, int, int]], optional): Fill color of the ellipse. Defaults to None.
            color (Union[str, int, Tuple[int, int, int]], optional): Alias of fill.
            outline (Union[str, int, Tuple[int, int, int]], optional): Outline color of the ellipse. Defaults to None.
            stroke_width (float, optional): Width of the outline. Defaults to 1.
        
        Returns:
            Editor: Editor object
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
        """Draw polygon into image
        
        Args:
            cordinates (list): Cordinates of the polygon
            fill (Union[str, int, Tuple[int, int, int]], optional): Fill color of the polygon. Defaults to None.
            color (Union[str, int, Tuple[int, int, int]], optional): Alias of fill.
            outline (Union[str, int, Tuple[int, int, int]], optional): Outline color of the polygon. Defaults to None.
        
        Returns:
            Editor: Editor object
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
        """Draw arc into image
        
        Args:
            position (Tuple[float, float]): Position to draw arc
            width (float): Width of the arc
            height (float): Height of the arc
            start (float): Start angle of the arc
            rotation (float): Rotation of the arc
            fill (Union[str, int, Tuple[int, int, int]], optional): Fill color of the arc. Defaults to None.
            color (Union[str, int, Tuple[int, int, int]], optional): Alias of fill.
            stroke_width (float, optional): Width of the outline. Defaults to 1.

        Returns:
            Editor: Editor object
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
        
        Args:
            fp (str): File path to save image
            format (str, optional): Image format. Defaults to None.
        """
        self.image.save(fp, format, **params)
