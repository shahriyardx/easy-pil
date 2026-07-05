"""Editor module."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any, Literal

from PIL import Image as PilImage
from PIL import ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from PIL.Image import Image

from .canvas import Canvas, Color
from .effect import Effect
from .font import Font
from .gradient import Gradient
from .text import Text


class Editor:
    """
    Editor class. It does all the editing operations.

    Parameters
    ----------
    source : Image | str | bytes | BytesIO | Editor | Canvas | Path
        Image or Canvas to edit.

    """

    def __init__(
        self,
        source: Image | str | bytes | BytesIO | Editor | Canvas | Path,
    ) -> None:
        """
        Initialize Editor.

        Parameters
        ----------
        source : Image | str | bytes | BytesIO | Editor | Canvas | Path
            Image or Canvas to edit.

        """
        if isinstance(source, bytes):
            source = BytesIO(source)

        if isinstance(source, (str, BytesIO, Path)):
            image = PilImage.open(source)
            self.image = image.convert("RGBA")
            image.close()
        elif isinstance(source, (Canvas, Editor)):
            self.image = source.image.convert("RGBA")
        else:
            self.image = source.convert("RGBA")

    def __enter__(self) -> Editor:
        """Context manager entry."""
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit — close image."""
        self.close()

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
        self.image.save(_bytes, "png")

        _ = _bytes.seek(0)
        return _bytes

    def close(self) -> None:
        """Close the image."""
        self.image.close()

    def resize(self, size: tuple[int, int], *, crop: bool = False) -> Editor:
        """
        Resize image.

        Parameters
        ----------
        size : Tuple[int, int]
            New Size of image
        crop : bool, optional
            Crop the image to bypass distortion, by default False

        """
        if not crop:
            self.image = self.image.resize(size, PilImage.Resampling.LANCZOS)
        else:
            width, height = self.image.size
            ideal_width, ideal_height = size

            aspect = width / height
            ideal_aspect = ideal_width / ideal_height

            if aspect > ideal_aspect:
                new_width = ideal_aspect * height
                offset = int((width - new_width) / 2)
                resize = (offset, 0, width - offset, height)
            else:
                new_height = width / ideal_aspect
                offset = int((height - new_height) / 2)
                resize = (0, offset, width, height - offset)

            self.image = self.image.crop(resize).resize(
                (ideal_width, ideal_height),
                PilImage.Resampling.LANCZOS,
            )

        return self

    def rounded_corners(self, radius: int = 10, offset: int = 2) -> Editor:
        """
        Make image rounded corners.

        Parameters
        ----------
        radius : int, optional
            Radius of roundness, by default 10
        offset : int, optional
            Offset pixel while making rounded, by default 2

        """
        background = PilImage.new(
            "RGBA",
            size=self.image.size,
            color=(255, 255, 255, 0),
        )
        holder = PilImage.new(
            "RGBA",
            size=self.image.size,
            color=(255, 255, 255, 0),
        )
        mask = PilImage.new(
            "RGBA",
            size=self.image.size,
            color=(255, 255, 255, 0),
        )
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            (offset, offset, self.image.size[0] - offset, self.image.size[1] - offset),
            radius=radius,
            fill="black",
        )
        holder.paste(self.image, (0, 0))
        self.image = PilImage.composite(holder, background, mask)

        background.close()
        holder.close()
        mask.close()

        return self

    def circle_image(self) -> Editor:
        """Make image circle."""
        background = PilImage.new(
            "RGBA",
            size=self.image.size,
            color=(255, 255, 255, 0),
        )
        holder = PilImage.new(
            "RGBA",
            size=self.image.size,
            color=(255, 255, 255, 0),
        )
        mask = PilImage.new(
            "RGBA",
            size=self.image.size,
            color=(255, 255, 255, 0),
        )
        mask_draw = ImageDraw.Draw(mask)
        ellipse_size = tuple(i - 1 for i in self.image.size)
        mask_draw.ellipse((0, 0, *ellipse_size), fill="black")
        holder.paste(self.image, (0, 0))
        self.image = PilImage.composite(holder, background, mask)

        background.close()
        holder.close()
        mask.close()

        return self

    def rotate(self, deg: float = 0, *, expand: bool = False) -> Editor:
        """
        Rotate image.

        Parameters
        ----------
        deg : float, optional
            Degrees to rotate, by default 0
        expand : bool, optional
            Expand while rotating, by default False

        """
        self.image = self.image.rotate(deg, expand=expand)
        return self

    def blur(
        self,
        mode: Literal["box", "gaussian"] = "gaussian",
        amount: float = 1,
    ) -> Editor:
        """
        Blur image.

        Parameters
        ----------
        mode : Literal["box", "gaussian"], optional
            Blur mode, by default "gaussian"
        amount : float, optional
            Amount of blur, by default 1

        """
        if mode == "box":
            self.image = self.image.filter(ImageFilter.BoxBlur(radius=amount))
        elif mode == "gaussian":
            self.image = self.image.filter(
                ImageFilter.GaussianBlur(radius=amount),
            )

        return self

    def blend(
        self,
        image: Image | Editor | Canvas,
        alpha: float = 0.0,
        *,
        on_top: bool = False,
    ) -> Editor:
        """
        Blend image into editor image.

        Parameters
        ----------
        image : Union[Image, Editor, Canvas]
            Image to blend
        alpha : float, optional
            Alpha amount, by default 0.0
        on_top : bool, optional
            Places image on top, by default False

        """
        pil_image = image.image if isinstance(image, (Editor, Canvas)) else image

        if pil_image.size != self.image.size:
            pil_image = Editor(pil_image).resize(self.image.size, crop=True).image

        if on_top:
            self.image = PilImage.blend(self.image, pil_image, alpha=alpha)
        else:
            self.image = PilImage.blend(pil_image, self.image, alpha=alpha)

        return self

    def paste(
        self,
        image: Image | Editor | Canvas,
        position: tuple[int, int],
    ) -> Editor:
        """
        Paste image into editor.

        Parameters
        ----------
        image : Union[Image, Editor, Canvas]
            Image to paste
        position : Tuple[int, int]
            Position to paste

        """
        blank = PilImage.new(
            "RGBA",
            size=self.image.size,
            color=(255, 255, 255, 0),
        )

        pil_image = image.image if isinstance(image, (Editor, Canvas)) else image

        blank.paste(pil_image, position)
        self.image = PilImage.alpha_composite(self.image, blank)

        blank.close()

        return self

    def text(
        self,
        position: tuple[float, float],
        text: str,
        font: ImageFont.FreeTypeFont | Font | None = None,
        color: Color = "black",
        align: Literal["left", "center", "right"] = "left",
        anchor: str | None = None,
        stroke_width: int | None = None,
        stroke_fill: Color = "black",
    ) -> Editor:
        """
        Draw text into image.

        Parameters
        ----------
        position : Tuple[float, float]
            Position to draw text.
        text : str
            Text to draw
        font : Union[ImageFont.FreeTypeFont, Font], optional
            Font used for text, by default None
        color : Color, optional
            Color of the font, by default "black"
        align : Literal["left", "center", "right"], optional
            Align text, by default "left"
        anchor : str, optional
            Pillow text anchor (e.g. "mm" for middle-middle). Overrides align if set.
        stroke_width : int, optional
            Whether there should be any stroke. Defaults to
            None. It represents the width of the said stroke.
        stroke_fill : Color, optional
            Color of the stroke, if any stroke is applied to the
            text. Defaults to "black"

        """
        if isinstance(font, Font):
            font = font.font

        anchors = {"left": "lt", "center": "mt", "right": "rt"}
        effective_anchor = anchor if anchor else anchors[align]

        draw = ImageDraw.Draw(self.image)

        if stroke_width:
            draw.text(
                position,
                text,
                color,
                font=font,
                anchor=effective_anchor,
                stroke_width=stroke_width,
                stroke_fill=stroke_fill,
            )
        else:
            draw.text(position, text, color, font=font, anchor=effective_anchor)

        return self

    def rich_text(
        self,
        position: tuple[float, float],
        texts: list[Text],
        *,
        space_separated: bool = True,
        align: Literal["left", "center", "right"] = "left",
        anchor: str | None = None,
    ) -> Editor:
        """
        Draw rich text with mixed colors and fonts inline.

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
        anchor : str, optional
            Pillow text anchor (e.g. "mm" for middle-middle). Defaults to
            align-based anchor ("lt"/"mt"/"rt").

        """
        draw = ImageDraw.Draw(self.image)

        if anchor is None:
            # align maps to anchor only when no manual position shifting occurs
            anchor = {"left": "lt", "center": "lt", "right": "lt"}[align]

        if align in ("right", "center"):
            total_width = 0

            for index, t in enumerate(texts):
                if space_separated and index != len(texts) - 1:
                    total_width += t.font.getlength(t.text + " ")
                else:
                    total_width += t.font.getlength(t.text)

            if align == "right":
                position = (int(position[0] - total_width), int(position[1]))
            else:
                position = (
                    int(position[0] - (total_width / 2)),
                    int(position[1]),
                )

        for text in texts:
            sentence = text.text
            font = text.font
            color = text.color
            seg_anchor = text.anchor if text.anchor else anchor

            if space_separated:
                width = font.getlength(sentence + " ")
            else:
                width = font.getlength(sentence)

            draw.text(position, sentence, color, font=font, anchor=seg_anchor)
            position = (int(position[0] + width), int(position[1]))

        return self

    def multi_text(
        self,
        position: tuple[float, float],
        texts: list[Text],
        *,
        space_separated: bool = True,
        align: Literal["left", "center", "right"] = "left",
        anchor: str | None = None,
    ) -> Editor:
        """Backward-compatible alias for :meth:`rich_text`."""
        return self.rich_text(
            position,
            texts,
            space_separated=space_separated,
            align=align,
            anchor=anchor,
        )

    def text_box(
        self,
        position: tuple[float, float],
        text: str,
        font: ImageFont.FreeTypeFont | Font,
        *,
        color: Color = "black",
        align: Literal["left", "center", "right"] = "left",
        max_width: float | None = None,
        line_spacing: int = 4,
        stroke_width: int | None = None,
        stroke_fill: Color = "black",
    ) -> Editor:
        """
        Draw text wrapped to fit inside a bounding box.

        Parameters
        ----------
        position : Tuple[float, float]
            Position to draw text (top-left).
        text : str
            Text to draw.
        font : Union[ImageFont.FreeTypeFont, Font]
            Font used for text.
        color : Color, optional
            Color of the font, by default "black"
        align : Literal["left", "center", "right"], optional
            Align text, by default "left"
        max_width : float, optional
            Max width before wrapping. Defaults to image width.
        line_spacing : int, optional
            Extra spacing between lines, by default 4
        stroke_width : int, optional
            Stroke width, by default None
        stroke_fill : Color, optional
            Stroke color, by default "black"

        """
        if isinstance(font, Font):
            font = font.font

        if max_width is None:
            max_width = float(self.image.width)

        draw = ImageDraw.Draw(self.image)
        x, y = position
        line = ""

        for word in text.split():
            test_line = f"{line} {word}".strip()
            w = font.getlength(test_line)

            if w > max_width and line:
                if align == "center":
                    cx = x + (max_width - font.getlength(line)) / 2
                elif align == "right":
                    cx = x + max_width - font.getlength(line)
                else:
                    cx = float(x)

                if stroke_width:
                    draw.text(
                        (cx, y),
                        line,
                        color,
                        font=font,
                        stroke_width=stroke_width,
                        stroke_fill=stroke_fill,
                    )
                else:
                    draw.text((cx, y), line, color, font=font)
                y += font.getbbox(line)[3] + line_spacing
                line = word
            else:
                line = test_line

        if line:
            if align == "center":
                cx = x + (max_width - font.getlength(line)) / 2
            elif align == "right":
                cx = x + max_width - font.getlength(line)
            else:
                cx = float(x)

            if stroke_width:
                draw.text(
                    (cx, y),
                    line,
                    color,
                    font=font,
                    stroke_width=stroke_width,
                    stroke_fill=stroke_fill,
                )
            else:
                draw.text((cx, y), line, color, font=font)

        return self

    def text_shadow(
        self,
        position: tuple[float, float],
        text: str,
        font: ImageFont.FreeTypeFont | Font | None = None,
        *,
        color: Color = "white",
        shadow_color: Color = "black",
        shadow_offset: tuple[int, int] = (2, 2),
        align: Literal["left", "center", "right"] = "left",
        stroke_width: int | None = None,
        stroke_fill: Color = "black",
    ) -> Editor:
        """
        Draw text with a drop shadow.

        Parameters
        ----------
        position : Tuple[float, float]
            Position to draw text.
        text : str
            Text to draw.
        font : Union[ImageFont.FreeTypeFont, Font], optional
            Font used for text, by default None
        color : Color, optional
            Text color, by default "white"
        shadow_color : Color, optional
            Shadow color, by default "black"
        shadow_offset : Tuple[int, int], optional
            Shadow offset (x, y), by default (2, 2)
        align : Literal["left", "center", "right"], optional
            Align text, by default "left"
        stroke_width : int, optional
            Stroke width, by default None
        stroke_fill : Color, optional
            Stroke color, by default "black"

        """
        shadow_pos = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])
        self.text(shadow_pos, text, font, color=shadow_color, align=align)
        return self.text(
            position,
            text,
            font,
            color=color,
            align=align,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )

    def rectangle(
        self,
        position: tuple[float, float],
        width: float,
        height: float,
        fill: Color | Gradient | None = None,
        color: Color | Gradient | None = None,
        outline: Color | None = None,
        stroke_width: int = 1,
        radius: int = 0,
    ) -> Editor:
        """
        Draw rectangle into image.

        Parameters
        ----------
        position : Tuple[float, float]
            Position to draw rectangle
        width : float
            Width of rectangle
        height : float
            Height of rectangle
        fill : Color or Gradient, optional
            Fill color or gradient, by default None
        color : Color or Gradient, optional
            Alias of fill, by default None
        outline : Color, optional
            Outline color, by default None
        stroke_width : float, optional
            Stroke width, by default 1
        radius : int, optional
            Radius of rectangle, by default 0

        """
        if color:
            fill = color

        if isinstance(fill, Gradient):
            x, y = position
            x2 = width + x
            y2 = height + y
            if outline:
                draw = ImageDraw.Draw(self.image)
                if radius <= 0:
                    draw.rectangle((x, y, x2, y2), outline=outline, width=stroke_width)
                else:
                    draw.rounded_rectangle(
                        (x, y, x2, y2),
                        radius=radius,
                        outline=outline,
                        width=stroke_width,
                    )
            if radius <= 0:
                self._apply_gradient_fill(
                    x,
                    y,
                    x2,
                    y2,
                    fill,
                    lambda d, w, h: d.rectangle((0, 0, w, h), fill=255),
                )
            else:
                self._apply_gradient_fill(
                    x,
                    y,
                    x2,
                    y2,
                    fill,
                    lambda d, w, h: d.rounded_rectangle(
                        (0, 0, w, h), radius=radius, fill=255
                    ),
                )
            return self

        draw = ImageDraw.Draw(self.image)

        to_width = width + position[0]
        to_height = height + position[1]

        if radius <= 0:
            draw.rectangle(
                (*position, to_width, to_height),
                fill=fill,
                outline=outline,
                width=stroke_width,
            )
        else:
            draw.rounded_rectangle(
                (*position, to_width, to_height),
                radius=radius,
                fill=fill,
                outline=outline,
                width=stroke_width,
            )

        return self

    def bar(
        self,
        position: tuple[int, int],
        max_width: float,
        height: float,
        percentage: int = 1,
        fill: Color | Gradient | None = None,
        color: Color | Gradient | None = None,
        outline: Color | None = None,
        stroke_width: int = 1,
        radius: int = 0,
    ) -> Editor:
        """
        Draw a progress bar.

        Parameters
        ----------
        position : Tuple[int, int]
            Position to draw bar
        max_width : Union[int, float]
            Max width of the bar
        height : Union[int, float]
            Height of the bar
        percentage : int, optional
            Percentage to fill of the bar, by default 1
        fill : Color or Gradient, optional
            Fill color or gradient, by default None
        color : Color or Gradient, optional
            Alias of fill, by default None
        outline : Color, optional
            Outline color, by default None
        stroke_width : float, optional
            Stroke width, by default 1
        radius : int, optional
            Radius of the bar, by default 0

        """
        if percentage == 0:
            return self

        if color:
            fill = color

        if percentage > 100 or percentage < 0:
            msg = "Percentage must be between 0 and 100"
            raise ValueError(msg)

        bw = int(max_width)
        bh = int(height)
        bar_width = int((max_width / 100) * percentage)

        bg = PilImage.new("RGBA", (bw, bh), (0, 0, 0, 0))
        main = PilImage.new("RGBA", (bw, bh), (0, 0, 0, 0))

        if isinstance(fill, Gradient):
            grad_img = fill.render(bar_width, bh)
            if radius > 0:
                fill_mask = PilImage.new("L", (bar_width, bh), 0)
                fill_draw = ImageDraw.Draw(fill_mask)
                fill_draw.rounded_rectangle(
                    (0, 0, bar_width, bh),
                    radius=radius,
                    fill=255,
                )
                main.paste(grad_img, (0, 0), fill_mask)
            else:
                main.paste(grad_img, (0, 0))
            if outline:
                main_draw = ImageDraw.Draw(main)
                if radius <= 0:
                    main_draw.rectangle(
                        (0, 0, bar_width, bh),
                        outline=outline,
                        width=stroke_width,
                    )
                else:
                    main_draw.rounded_rectangle(
                        (0, 0, bar_width, bh),
                        radius=radius,
                        outline=outline,
                        width=stroke_width,
                    )
        else:
            main_draw = ImageDraw.Draw(main)
            if radius <= 0:
                main_draw.rectangle(
                    (0, 0, bar_width, bh),
                    fill=fill,
                    outline=outline,
                    width=stroke_width,
                )
            else:
                main_draw.rounded_rectangle(
                    (0, 0, bar_width, bh),
                    radius=radius,
                    fill=fill,
                    outline=outline,
                    width=stroke_width,
                )

        mask = PilImage.new("L", (bw, bh), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            (0, 0, bw, bh),
            radius=radius,
            fill=255,
            outline=255,
            width=stroke_width,
        )

        final = PilImage.composite(main, bg, mask)
        _ = self.paste(final, position)

        main.close()
        final.close()
        bg.close()
        mask.close()

        return self

    def rounded_bar(
        self,
        position: tuple[float, float],
        width: float,
        height: float,
        percentage: float,
        fill: Color | Gradient | None = None,
        color: Color | Gradient | None = None,
        stroke_width: int = 1,
        radius: int | None = None,
    ) -> Editor:
        """
        Draw a rounded bar.

        Parameters
        ----------
        position : Tuple[float, float]
            Position to draw rounded bar
        width : Union[int, float]
            Width of the bar
        height : Union[int, float]
            Height of the bar
        percentage : float
            Percentage to fill.
        fill : Color or Gradient, optional
            Fill color or gradient, by default None
        color : Color or Gradient, optional
            Alias of color, by default None
        stroke_width : float, optional
            Stroke width, by default 1
        radius : int, optional
            Corner radius. Defaults to height//2 (fully rounded).

        """
        if color:
            fill = color

        return self.bar(
            (int(position[0]), int(position[1])),
            width,
            height,
            percentage=int(percentage),
            fill=fill,
            stroke_width=stroke_width,
            radius=radius if radius is not None else int(height // 2),
        )

    def ellipse(
        self,
        position: tuple[float, float],
        width: float,
        height: float,
        fill: Color | Gradient | None = None,
        color: Color | Gradient | None = None,
        outline: Color | None = None,
        stroke_width: int = 1,
    ) -> Editor:
        """
        Draw an ellipse.

        Parameters
        ----------
        position : Tuple[float, float]
            Position to draw ellipse
        width : float
            Width of ellipse
        height : float
            Height of ellipse
        fill : Color or Gradient, optional
            Fill color or gradient, by default None
        color : Color or Gradient, optional
            Alias of fill, by default None
        outline : Color, optional
            Outline color, by default None
        stroke_width : float, optional
            Stroke width, by default 1

        """
        if color:
            fill = color

        if isinstance(fill, Gradient):
            x, y = position
            x2 = width + x
            y2 = height + y
            if outline:
                draw = ImageDraw.Draw(self.image)
                draw.ellipse((x, y, x2, y2), outline=outline, width=stroke_width)
            self._apply_gradient_fill(
                x,
                y,
                x2,
                y2,
                fill,
                lambda d, w, h: d.ellipse((0, 0, w, h), fill=255),
            )
            return self

        draw = ImageDraw.Draw(self.image)
        to_width = width + position[0]
        to_height = height + position[1]

        draw.ellipse(
            (*position, to_width, to_height),
            outline=outline,
            fill=fill,
            width=stroke_width,
        )

        return self

    def polygon(
        self,
        coordinates: list[tuple[int, int]],
        fill: Color | Gradient | None = None,
        color: Color | Gradient | None = None,
        outline: Color | None = None,
    ) -> Editor:
        """
        Draw a polygon.

        Parameters
        ----------
        coordinates : list
            Coordinates to draw
        fill : Color or Gradient, optional
            Fill color or gradient, by default None
        color : Color or Gradient, optional
            Alias of fill, by default None
        outline : Color, optional
            Outline color, by default None

        """
        if color:
            fill = color

        if isinstance(fill, Gradient):
            xs = [c[0] for c in coordinates]
            ys = [c[1] for c in coordinates]
            x1, y1 = min(xs), min(ys)
            x2, y2 = max(xs), max(ys)
            if outline:
                draw = ImageDraw.Draw(self.image)
                draw.polygon(coordinates, outline=outline)
            offset_coords = [(c[0] - x1, c[1] - y1) for c in coordinates]
            self._apply_gradient_fill(
                x1,
                y1,
                x2,
                y2,
                fill,
                lambda d, w, h: d.polygon(offset_coords, fill=255),
            )
            return self

        draw = ImageDraw.Draw(self.image)
        draw.polygon(coordinates, fill=fill, outline=outline)

        return self

    def arc(
        self,
        position: tuple[float, float],
        width: float,
        height: float,
        start: float,
        rotation: float,
        fill: Color | Gradient | None = None,
        color: Color | Gradient | None = None,
        stroke_width: int = 1,
    ) -> Editor:
        """
        Draw arc.

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
            Rotation in degree
        fill : Color or Gradient, optional
            Fill color or gradient, by default None
        color : Color or Gradient, optional
            Alias of fill, by default None
        stroke_width : float, optional
            Stroke width, by default 1

        """
        if color:
            fill = color

        start_angle = start - 90
        end_angle = rotation - 90

        if isinstance(fill, Gradient):
            x, y = position
            x2 = x + width
            y2 = y + height
            w = int(x2 - x)
            h = int(y2 - y)
            mask = PilImage.new("L", (w, h), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.arc(
                (0, 0, w, h), start_angle, end_angle, fill=255, width=stroke_width
            )
            grad_img = fill.render(w, h)
            self.image.paste(grad_img, (int(x), int(y)), mask)
            return self

        draw = ImageDraw.Draw(self.image)

        draw.arc(
            (*position, position[0] + width, position[1] + height),
            start_angle,
            end_angle,
            fill,
            width=stroke_width,
        )

        return self

    def show(self) -> None:
        """Show the image."""
        self.image.show()

    def save(
        self,
        fp: str | Path | BytesIO,
        file_format: str | None = None,
        **params: Any,
    ) -> None:
        """
        Save the image.

        Parameters
        ----------
        fp : str | Path | BytesIO
            File path or buffer
        file_format : str, optional
            File format, by default None
        **params : Any
            Additional parameters for PIL Image.save

        """
        self.image.save(fp, file_format, **params)

    @classmethod
    def open(cls, fp: str | Path | BytesIO) -> Editor:
        """
        Open image file as Editor.

        Parameters
        ----------
        fp : str | Path | BytesIO
            File path or buffer

        """
        return cls(fp)

    def to_bytes(self, fmt: str = "PNG") -> bytes:
        """
        Return image as bytes.

        Parameters
        ----------
        fmt : str, optional
            Image format, by default "PNG"

        """
        buf = BytesIO()
        image = self.image
        if fmt.upper() in ("JPEG", "JPG"):
            image = image.convert("RGB")
        image.save(buf, fmt)
        buf.seek(0)
        return buf.read()

    def crop(self, box: tuple[int, int, int, int]) -> Editor:
        """
        Crop image to bounding box.

        Parameters
        ----------
        box : tuple[int, int, int, int]
            (left, upper, right, lower) pixel coordinates

        """
        self.image = self.image.crop(box)
        return self

    def thumbnail(self, size: tuple[int, int]) -> Editor:
        """
        Resize image to fit within size, maintaining aspect ratio.

        Parameters
        ----------
        size : tuple[int, int]
            Maximum (width, height)

        """
        self.image.thumbnail(size, PilImage.Resampling.LANCZOS)
        return self

    def flip(self, *, horizontal: bool = False) -> Editor:
        """
        Flip image.

        Parameters
        ----------
        horizontal : bool, optional
            Flip horizontally (mirror), by default False (vertical flip)

        """
        if horizontal:
            self.image = self.image.transpose(PilImage.Transpose.FLIP_LEFT_RIGHT)
        else:
            self.image = self.image.transpose(PilImage.Transpose.FLIP_TOP_BOTTOM)
        return self

    def invert(self) -> Editor:
        """Invert image colors."""
        self.image = ImageOps.invert(self.image.convert("RGB")).convert("RGBA")
        return self

    def mask(self, mask_image: Image | Editor, invert: bool = False) -> Editor:
        """
        Apply external mask for transparency.

        Parameters
        ----------
        mask_image : Union[Image, Editor]
            Grayscale mask where white=opaque, black=transparent.
        invert : bool, optional
            Invert mask (white=transparent, black=opaque), by default False

        """
        if isinstance(mask_image, Editor):
            mask_image = mask_image.image

        mask_img = mask_image.convert("L").resize(
            self.image.size, PilImage.Resampling.LANCZOS
        )
        if invert:
            mask_img = ImageOps.invert(mask_img)

        self.image.putalpha(mask_img)
        return self

    def contrast(self, factor: float = 1.0) -> Editor:
        """
        Adjust image contrast.

        Parameters
        ----------
        factor : float, optional
            Contrast factor. 1.0 = original, >1 = more contrast, <1 = less.

        """
        self.image = ImageEnhance.Contrast(self.image).enhance(factor)
        return self

    def brightness(self, factor: float = 1.0) -> Editor:
        """
        Adjust image brightness.

        Parameters
        ----------
        factor : float, optional
            Brightness factor. 1.0 = original, >1 = brighter, <1 = darker.

        """
        self.image = ImageEnhance.Brightness(self.image).enhance(factor)
        return self

    def saturation(self, factor: float = 1.0) -> Editor:
        """
        Adjust image color saturation.

        Parameters
        ----------
        factor : float, optional
            Saturation factor. 1.0 = original, >1 = more saturated, <1 = less.

        """
        self.image = ImageEnhance.Color(self.image).enhance(factor)
        return self

    def line(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        width: int = 1,
        fill: Color = "black",
    ) -> Editor:
        """
        Draw a line.

        Parameters
        ----------
        start : tuple[float, float]
            Start coordinates (x, y)
        end : tuple[float, float]
            End coordinates (x, y)
        width : int, optional
            Line width, by default 1
        fill : Color, optional
            Line color, by default "black"

        """
        draw = ImageDraw.Draw(self.image)
        draw.line((*start, *end), fill=fill, width=width)
        return self

    def donut(
        self,
        position: tuple[float, float],
        inner_radius: float,
        outer_radius: float,
        fill: Color | Gradient = "black",
        outline: Color | None = None,
        stroke_width: int = 0,
    ) -> Editor:
        """
        Draw a donut (ring) shape.

        Parameters
        ----------
        position : tuple[float, float]
            Center coordinates (x, y)
        inner_radius : float
            Inner radius of ring
        outer_radius : float
            Outer radius of ring
        fill : Color or Gradient, optional
            Fill color or gradient, by default "black"
        outline : Color | None, optional
            Outline color, by default None
        stroke_width : int, optional
            Outline stroke width, by default 0

        """
        x, y = position
        x1, y1 = x - outer_radius, y - outer_radius
        x2, y2 = x + outer_radius, y + outer_radius

        if isinstance(fill, Gradient):
            w = int(x2 - x1)
            h = int(y2 - y1)
            ir = int(inner_radius)
            mask = PilImage.new("L", (w, h), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, w, h), fill=255)
            cx, cy = w // 2, h // 2
            mask_draw.ellipse(
                (cx - ir, cy - ir, cx + ir, cy + ir),
                fill=0,
            )
            if outline:
                draw = ImageDraw.Draw(self.image)
                draw.ellipse(
                    (x1, y1, x2, y2),
                    outline=outline,
                    width=stroke_width,
                )
            grad_img = fill.render(w, h)
            self.image.paste(grad_img, (int(x1), int(y1)), mask)
            return self

        layer = PilImage.new("RGBA", self.image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        draw.ellipse(
            (x1, y1, x2, y2),
            fill=fill,
            outline=outline,
            width=stroke_width,
        )
        draw.ellipse(
            (x - inner_radius, y - inner_radius, x + inner_radius, y + inner_radius),
            fill=(0, 0, 0, 0),
        )
        self.image = PilImage.alpha_composite(self.image, layer)
        return self

    def add_border(
        self,
        width: int = 1,
        color: Color = "black",
    ) -> Editor:
        """
        Add a border around the image.

        Parameters
        ----------
        width : int, optional
            Border width in pixels, by default 1
        color : Color, optional
            Border color, by default "black"

        """
        new_size = (
            self.image.width + width * 2,
            self.image.height + width * 2,
        )
        bg = PilImage.new("RGBA", new_size, color)
        bg.paste(self.image, (width, width))
        self.image = bg
        return self

    def fit_text(
        self,
        text: str,
        max_width: float,
        font: ImageFont.FreeTypeFont | Font | str,
        *,
        max_size: int = 100,
        min_size: int = 1,
    ) -> ImageFont.FreeTypeFont:
        """
        Find the largest font size that fits text within max_width.

        Parameters
        ----------
        text : str
            Text to measure
        max_width : float
            Maximum allowed width in pixels
        font : ImageFont.FreeTypeFont | Font | str
            Font object or path to font file
        max_size : int, optional
            Maximum font size to try, by default 100
        min_size : int, optional
            Minimum font size to try, by default 1

        Returns
        -------
        ImageFont.FreeTypeFont
            Font at the fitted size

        """
        if isinstance(font, Font):
            font_path = font.font.path
        elif isinstance(font, ImageFont.FreeTypeFont):
            font_path = font.path
        else:
            font_path = font

        best_size = min_size
        low = min_size
        high = max_size
        while low <= high:
            mid = (low + high) // 2
            ft_font = ImageFont.truetype(font_path, size=mid)
            bbox = ft_font.getbbox(text)
            if bbox[2] - bbox[0] <= max_width:
                best_size = mid
                low = mid + 1
            else:
                high = mid - 1

        return ImageFont.truetype(font_path, size=best_size)

    def centered_text(
        self,
        text: str,
        font: ImageFont.FreeTypeFont | Font | None = None,
        color: Color = "black",
        *,
        y_offset: float = 0,
    ) -> Editor:
        """
        Draw text centered horizontally on the image.

        Parameters
        ----------
        text : str
            Text to draw
        font : ImageFont.FreeTypeFont | Font, optional
            Font for text
        color : Color, optional
            Text color, by default "black"
        y_offset : float, optional
            Vertical offset from center, by default 0

        """
        if isinstance(font, Font):
            font = font.font

        draw = ImageDraw.Draw(self.image)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.image.width - text_width) / 2
        y = (self.image.height - (bbox[3] - bbox[1])) / 2 + y_offset
        draw.text((x, y), text, color, font=font)

        return self

    def compose(
        self,
        editors: list[Editor],
        direction: Literal["horizontal", "vertical"] = "vertical",
        align: Literal["start", "center", "end"] = "center",
        spacing: int = 0,
    ) -> Editor:
        """
        Combine multiple editors into one image.

        Parameters
        ----------
        editors : list[Editor]
            Editors to combine
        direction : Literal["horizontal", "vertical"], optional
            Layout direction, by default "vertical"
        align : Literal["start", "center", "end"], optional
            Alignment of items in the opposite axis, by default "center"
        spacing : int, optional
            Spacing between items in pixels, by default 0

        """
        images = [e.image for e in editors]

        if direction == "vertical":
            total_w = max(img.width for img in images)
            total_h = sum(img.height for img in images) + spacing * (len(images) - 1)
            canvas = PilImage.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
            y = 0
            for img in images:
                x = {0: 0, 1: (total_w - img.width) // 2, 2: total_w - img.width}[
                    ["start", "center", "end"].index(align)
                ]
                canvas.paste(img, (x, y), img)
                y += img.height + spacing
        else:
            total_w = sum(img.width for img in images) + spacing * (len(images) - 1)
            total_h = max(img.height for img in images)
            canvas = PilImage.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
            x = 0
            for img in images:
                y = {0: 0, 1: (total_h - img.height) // 2, 2: total_h - img.height}[
                    ["start", "center", "end"].index(align)
                ]
                canvas.paste(img, (x, y), img)
                x += img.width + spacing

        self.image = canvas
        return self

    def effect(
        self,
        effect: Effect,
    ) -> Editor:
        """Apply effect to image. Accepts any Effect subclass instance."""
        self.image = effect.apply(self.image)
        return self

    def _apply_gradient_fill(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        gradient: Gradient,
        draw_mask,
    ) -> None:
        """Render gradient clipped to shape mask, composite onto image."""
        w = int(x2 - x1)
        h = int(y2 - y1)
        if w <= 0 or h <= 0:
            return
        mask = PilImage.new("L", (w, h), 0)
        mask_draw = ImageDraw.Draw(mask)
        draw_mask(mask_draw, w, h)
        grad_img = gradient.render(w, h)
        self.image.paste(grad_img, (int(x1), int(y1)), mask)
