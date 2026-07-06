"""Editor module."""

from __future__ import annotations

import math
from io import BytesIO
from pathlib import Path
from typing import Any, Literal

import numpy as np
from PIL import Image as PilImage
from PIL import (
    ImageChops,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont,
    ImageOps,
)
from PIL.Image import Image

from ._nputil import as_rgba, from_array
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

        self.last_text_bbox: tuple[int, int, int, int] = (0, 0, 0, 0)

    @property
    def last_text_size(self) -> tuple[int, int]:
        """
        Return (width, height) of the last drawn text.

        Returns
        -------
        tuple[int, int]
            Width and height of :attr:`last_text_bbox`.

        """
        left, top, right, bottom = self.last_text_bbox
        return (right - left, bottom - top)

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

    def _replace(self, new: Image) -> None:
        """Swap in a new owned buffer, closing the old owned one."""
        old = self.image
        self.image = new
        if old is not new:
            try:
                old.close()
            except Exception:  # noqa: BLE001, S110
                pass

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
            self._replace(self.image.resize(size, PilImage.Resampling.LANCZOS))
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

            self._replace(
                self.image.crop(resize).resize(
                    (ideal_width, ideal_height),
                    PilImage.Resampling.LANCZOS,
                ),
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
        self._replace(PilImage.composite(holder, background, mask))

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
        self._replace(PilImage.composite(holder, background, mask))

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
        self._replace(self.image.rotate(deg, expand=expand))
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
            self._replace(self.image.filter(ImageFilter.BoxBlur(radius=amount)))
        elif mode == "gaussian":
            self._replace(
                self.image.filter(ImageFilter.GaussianBlur(radius=amount)),
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
            self._replace(PilImage.blend(self.image, pil_image, alpha=alpha))
        else:
            self._replace(PilImage.blend(pil_image, self.image, alpha=alpha))

        return self

    def _resolve_anchor(
        self,
        anchor: str,
        size: tuple[int, int],
    ) -> tuple[int, int]:
        """Resolve an anchor keyword to top-left pixel coords for a pasted image."""
        iw, ih = self.image.size
        pw, ph = size
        cx = (iw - pw) // 2
        cy = (ih - ph) // 2
        right = iw - pw
        bottom = ih - ph
        mapping = {
            "center": (cx, cy),
            "top-left": (0, 0),
            "top-right": (right, 0),
            "bottom-left": (0, bottom),
            "bottom-right": (right, bottom),
            "top": (cx, 0),
            "bottom": (cx, bottom),
            "left": (0, cy),
            "right": (right, cy),
        }
        if anchor not in mapping:
            msg = f"Unknown paste anchor: {anchor!r}"
            raise ValueError(msg)
        return mapping[anchor]

    def paste(
        self,
        image: Image | Editor | Canvas,
        position: tuple[int, int] | str,
        opacity: float = 1.0,
    ) -> Editor:
        """
        Paste image into editor.

        Parameters
        ----------
        image : Union[Image, Editor, Canvas]
            Image to paste
        position : Tuple[int, int] | str
            Position to paste. Either pixel coords, or an anchor keyword:
            "center", "top-left", "top-right", "bottom-left", "bottom-right",
            "top", "bottom", "left", "right".
        opacity : float, optional
            Opacity of pasted image (0.0-1.0), by default 1.0. When < 1 the
            pasted image alpha is scaled before compositing.

        """
        blank = PilImage.new(
            "RGBA",
            size=self.image.size,
            color=(255, 255, 255, 0),
        )

        pil_image = image.image if isinstance(image, (Editor, Canvas)) else image

        if isinstance(position, str):
            position = self._resolve_anchor(position, pil_image.size)

        if opacity < 1.0:
            # as_rgba returns a fresh image only when a convert happened; if it
            # handed back the caller's own RGBA image, copy so putalpha does not
            # mutate it.
            rgba = as_rgba(pil_image)
            if rgba is pil_image:
                rgba = rgba.copy()
            alpha = rgba.getchannel("A").point(
                lambda a: int(a * opacity),
            )
            rgba.putalpha(alpha)
            pil_image = rgba

        blank.paste(pil_image, position)
        self._replace(PilImage.alpha_composite(self.image, blank))

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

        bbox = draw.textbbox(
            position,
            text,
            font=font,
            anchor=effective_anchor,
            stroke_width=stroke_width or 0,
        )
        self.last_text_bbox = (
            int(bbox[0]),
            int(bbox[1]),
            int(bbox[2]),
            int(bbox[3]),
        )

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

        seg_bboxes = []
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
            seg_bboxes.append(
                draw.textbbox(position, sentence, font=font, anchor=seg_anchor),
            )
            position = (int(position[0] + width), int(position[1]))

        if seg_bboxes:
            self.last_text_bbox = (
                int(min(b[0] for b in seg_bboxes)),
                int(min(b[1] for b in seg_bboxes)),
                int(max(b[2] for b in seg_bboxes)),
                int(max(b[3] for b in seg_bboxes)),
            )

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
        drawn_bboxes = []

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
                drawn_bboxes.append(
                    draw.textbbox(
                        (cx, y),
                        line,
                        font=font,
                        stroke_width=stroke_width or 0,
                    ),
                )
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
            drawn_bboxes.append(
                draw.textbbox(
                    (cx, y),
                    line,
                    font=font,
                    stroke_width=stroke_width or 0,
                ),
            )

        if drawn_bboxes:
            self.last_text_bbox = (
                int(min(b[0] for b in drawn_bboxes)),
                int(min(b[1] for b in drawn_bboxes)),
                int(max(b[2] for b in drawn_bboxes)),
                int(max(b[3] for b in drawn_bboxes)),
            )

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
        outline: Color | Gradient | None = None,
        stroke_width: int = 1,
        radius: int = 0,
        *,
        segments: int = 0,
        show_percentage: bool = False,
        text_font: ImageFont.FreeTypeFont | Font | None = None,
        text_color: Color = "white",
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
        outline : Color or Gradient, optional
            Outline color or gradient, by default None
        stroke_width : float, optional
            Stroke width, by default 1
        radius : int, optional
            Radius of the bar, by default 0
        segments : int, optional
            When > 0, split the filled portion into this many equal chunks
            with a small gap between them, by default 0
        show_percentage : bool, optional
            Draw the integer percentage centered on the bar, by default False
        text_font : ImageFont.FreeTypeFont | Font, optional
            Font for the percentage text. Defaults to Poppins.
        text_color : Color, optional
            Color of the percentage text, by default "white"

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

        gap = 2
        if segments and segments > 0 and bar_width > 0:
            seg_total = bar_width - gap * (segments - 1)
            seg_w = seg_total / segments
            if seg_w < 1:
                seg_w = bar_width / segments
                gap = 0
            rects = []
            pos = 0.0
            for _ in range(segments):
                sx = int(round(pos))
                ex = min(int(round(pos + seg_w)), bar_width)
                if ex > sx:
                    rects.append((sx, 0, ex, bh))
                pos += seg_w + gap
        else:
            rects = [(0, 0, bar_width, bh)]

        def draw_shape(d: ImageDraw.ImageDraw, box, **kw) -> None:  # noqa: ANN001
            if radius > 0:
                d.rounded_rectangle(box, radius=radius, **kw)
            else:
                d.rectangle(box, **kw)

        outline_is_gradient = isinstance(outline, Gradient)
        solid_outline = None if outline_is_gradient else outline

        if isinstance(fill, Gradient):
            fill_mask = PilImage.new("L", (bw, bh), 0)
            fill_draw = ImageDraw.Draw(fill_mask)
            for r in rects:
                draw_shape(fill_draw, r, fill=255)
            grad_img = fill.render(bw, bh)
            main.paste(grad_img, (0, 0), fill_mask)
            if solid_outline:
                main_draw = ImageDraw.Draw(main)
                for r in rects:
                    draw_shape(
                        main_draw,
                        r,
                        outline=solid_outline,
                        width=stroke_width,
                    )
        else:
            main_draw = ImageDraw.Draw(main)
            for r in rects:
                draw_shape(
                    main_draw,
                    r,
                    fill=fill,
                    outline=solid_outline,
                    width=stroke_width,
                )

        if outline_is_gradient and bar_width > 0:
            outline_mask = PilImage.new("L", (bw, bh), 0)
            outline_draw = ImageDraw.Draw(outline_mask)
            for r in rects:
                draw_shape(outline_draw, r, outline=255, width=stroke_width)
            outline_grad = outline.render(bw, bh)
            main.paste(outline_grad, (0, 0), outline_mask)

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

        if show_percentage:
            label_font = text_font
            if label_font is None:
                label_font = Font.poppins(size=max(int(bh * 0.6), 1))
            if isinstance(label_font, Font):
                label_font = label_font.font
            final_draw = ImageDraw.Draw(final)
            final_draw.text(
                (bw / 2, bh / 2),
                f"{int(percentage)}%",
                fill=text_color,
                font=label_font,
                anchor="mm",
            )

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
        outline: Color | Gradient | None = None,
        stroke_width: int = 1,
        radius: int | None = None,
        *,
        segments: int = 0,
        show_percentage: bool = False,
        text_font: ImageFont.FreeTypeFont | Font | None = None,
        text_color: Color = "white",
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
        outline : Color or Gradient, optional
            Outline color or gradient, by default None
        stroke_width : float, optional
            Stroke width, by default 1
        radius : int, optional
            Corner radius. Defaults to height//2 (fully rounded).
        segments : int, optional
            When > 0, split the filled portion into this many chunks, by
            default 0
        show_percentage : bool, optional
            Draw the integer percentage centered on the bar, by default False
        text_font : ImageFont.FreeTypeFont | Font, optional
            Font for the percentage text. Defaults to Poppins.
        text_color : Color, optional
            Color of the percentage text, by default "white"

        """
        if color:
            fill = color

        return self.bar(
            (int(position[0]), int(position[1])),
            width,
            height,
            percentage=int(percentage),
            fill=fill,
            outline=outline,
            stroke_width=stroke_width,
            radius=radius if radius is not None else int(height // 2),
            segments=segments,
            show_percentage=show_percentage,
            text_font=text_font,
            text_color=text_color,
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

    def _draw_polygon_shape(
        self,
        points: list[tuple[float, float]],
        fill: Color | Gradient | None,
        outline: Color | None,
        stroke_width: int,
    ) -> Editor:
        """Draw a polygon from points supporting Color or Gradient fill."""
        if isinstance(fill, Gradient):
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            x1, y1 = min(xs), min(ys)
            x2, y2 = max(xs), max(ys)
            offset_coords = [(p[0] - x1, p[1] - y1) for p in points]
            self._apply_gradient_fill(
                x1,
                y1,
                x2,
                y2,
                fill,
                lambda d, w, h: d.polygon(offset_coords, fill=255),  # noqa: ARG005
            )
            if outline:
                draw = ImageDraw.Draw(self.image)
                draw.polygon(points, outline=outline, width=stroke_width)
            return self

        draw = ImageDraw.Draw(self.image)
        draw.polygon(points, fill=fill, outline=outline, width=stroke_width)
        return self

    def regular_polygon(
        self,
        center: tuple[float, float],
        sides: int,
        radius: float,
        rotation: float = 0,
        fill: Color | Gradient | None = None,
        color: Color | Gradient | None = None,
        outline: Color | None = None,
        stroke_width: int = 1,
    ) -> Editor:
        """
        Draw a regular n-sided polygon.

        Parameters
        ----------
        center : tuple[float, float]
            Center coordinates (x, y)
        sides : int
            Number of sides
        radius : float
            Circumscribed radius
        rotation : float, optional
            Rotation in degrees, by default 0
        fill : Color or Gradient, optional
            Fill color or gradient, by default None
        color : Color or Gradient, optional
            Alias of fill, by default None
        outline : Color, optional
            Outline color, by default None
        stroke_width : int, optional
            Stroke width, by default 1

        """
        if color:
            fill = color

        cx, cy = center
        base = math.radians(rotation - 90)
        points = [
            (
                cx + radius * math.cos(base + 2 * math.pi * i / sides),
                cy + radius * math.sin(base + 2 * math.pi * i / sides),
            )
            for i in range(sides)
        ]
        return self._draw_polygon_shape(points, fill, outline, stroke_width)

    def star(
        self,
        center: tuple[float, float],
        points: int,
        outer_radius: float,
        inner_radius: float,
        rotation: float = 0,
        fill: Color | Gradient | None = None,
        color: Color | Gradient | None = None,
        outline: Color | None = None,
        stroke_width: int = 1,
    ) -> Editor:
        """
        Draw a star polygon.

        Parameters
        ----------
        center : tuple[float, float]
            Center coordinates (x, y)
        points : int
            Number of star points
        outer_radius : float
            Radius of outer vertices
        inner_radius : float
            Radius of inner vertices
        rotation : float, optional
            Rotation in degrees, by default 0
        fill : Color or Gradient, optional
            Fill color or gradient, by default None
        color : Color or Gradient, optional
            Alias of fill, by default None
        outline : Color, optional
            Outline color, by default None
        stroke_width : int, optional
            Stroke width, by default 1

        """
        if color:
            fill = color

        cx, cy = center
        base = math.radians(rotation - 90)
        verts = []
        for i in range(points * 2):
            r = outer_radius if i % 2 == 0 else inner_radius
            ang = base + math.pi * i / points
            verts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        return self._draw_polygon_shape(verts, fill, outline, stroke_width)

    def triangle(
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
        Draw an upward triangle within the given bounding box.

        Parameters
        ----------
        position : tuple[float, float]
            Top-left of the bounding box
        width : float
            Width of the bounding box
        height : float
            Height of the bounding box
        fill : Color or Gradient, optional
            Fill color or gradient, by default None
        color : Color or Gradient, optional
            Alias of fill, by default None
        outline : Color, optional
            Outline color, by default None
        stroke_width : int, optional
            Stroke width, by default 1

        """
        if color:
            fill = color

        x, y = position
        points = [
            (x + width / 2, y),
            (x, y + height),
            (x + width, y + height),
        ]
        return self._draw_polygon_shape(points, fill, outline, stroke_width)

    def squircle(
        self,
        position: tuple[float, float],
        width: float,
        height: float,
        radius_ratio: float = 0.4,
        fill: Color | Gradient | None = None,
        color: Color | Gradient | None = None,
        outline: Color | None = None,
        stroke_width: int = 1,
    ) -> Editor:
        """
        Draw a squircle (superellipse / iOS rounded square).

        Parameters
        ----------
        position : tuple[float, float]
            Top-left of the bounding box
        width : float
            Width of the bounding box
        height : float
            Height of the bounding box
        radius_ratio : float, optional
            Roundness ratio (higher = rounder), by default 0.4
        fill : Color or Gradient, optional
            Fill color or gradient, by default None
        color : Color or Gradient, optional
            Alias of fill, by default None
        outline : Color, optional
            Outline color, by default None
        stroke_width : int, optional
            Stroke width, by default 1

        """
        if color:
            fill = color

        x, y = position
        w = int(width)
        h = int(height)
        if w <= 0 or h <= 0:
            return self

        n = max(2.0, 2.0 / max(radius_ratio, 0.01))
        mask = self._superellipse_mask(w, h, n)

        if isinstance(fill, Gradient):
            grad = fill.render(w, h)
            self.image.paste(grad, (int(x), int(y)), mask)
        elif fill:
            layer = PilImage.new("RGBA", (w, h), fill)
            self.image.paste(layer, (int(x), int(y)), mask)

        if outline:
            inner = self._superellipse_mask(w, h, n, inset=float(stroke_width))
            ring = ImageChops.subtract(mask, inner)
            oc = PilImage.new("RGBA", (w, h), outline)
            self.image.paste(oc, (int(x), int(y)), ring)

        return self

    def _superellipse_mask(
        self,
        w: int,
        h: int,
        n: float,
        inset: float = 0.0,
    ) -> Image:
        """Return an L-mode superellipse mask of size (w, h)."""
        a = w / 2 - inset
        b = h / 2 - inset
        if a <= 0 or b <= 0:
            return PilImage.new("L", (w, h), 0)
        cx = w / 2
        cy = h / 2
        ys, xs = np.meshgrid(
            np.arange(h, dtype=np.float64),
            np.arange(w, dtype=np.float64),
            indexing="ij",
        )
        nx = np.abs((xs + 0.5 - cx) / a) ** n
        ny = np.abs((ys + 0.5 - cy) / b) ** n
        mask = ((nx + ny) <= 1).astype(np.uint8) * 255
        return from_array(mask, "L")

    def speech_bubble(
        self,
        position: tuple[float, float],
        width: float,
        height: float,
        tail: str = "bottom-left",
        radius: int = 12,
        fill: Color | Gradient | None = None,
        color: Color | Gradient | None = None,
        outline: Color | None = None,
        stroke_width: int = 1,
    ) -> Editor:
        """
        Draw a rounded speech bubble with a triangular tail.

        Parameters
        ----------
        position : tuple[float, float]
            Top-left of the bubble body
        width : float
            Width of the bubble body
        height : float
            Height of the bubble body
        tail : str, optional
            Side of the tail: "bottom-left", "bottom-right", "bottom",
            "top-left", "top-right", "top", "left", "right", by default
            "bottom-left"
        radius : int, optional
            Corner radius, by default 12
        fill : Color or Gradient, optional
            Fill color or gradient, by default None
        color : Color or Gradient, optional
            Alias of fill, by default None
        outline : Color, optional
            Outline color, by default None
        stroke_width : int, optional
            Stroke width, by default 1

        """
        if color:
            fill = color

        x, y = position
        x2 = x + width
        y2 = y + height
        t = max(radius, 10)
        body = (x, y, x2, y2)
        tails = {
            "bottom-left": [
                (x + radius, y2),
                (x + radius + t, y2),
                (x + radius, y2 + t),
            ],
            "bottom-right": [
                (x2 - radius - t, y2),
                (x2 - radius, y2),
                (x2 - radius, y2 + t),
            ],
            "bottom": [
                (x + width / 2 - t / 2, y2),
                (x + width / 2 + t / 2, y2),
                (x + width / 2, y2 + t),
            ],
            "top-left": [(x + radius, y), (x + radius + t, y), (x + radius, y - t)],
            "top-right": [(x2 - radius - t, y), (x2 - radius, y), (x2 - radius, y - t)],
            "top": [
                (x + width / 2 - t / 2, y),
                (x + width / 2 + t / 2, y),
                (x + width / 2, y - t),
            ],
            "left": [
                (x, y + height / 2 - t / 2),
                (x, y + height / 2 + t / 2),
                (x - t, y + height / 2),
            ],
            "right": [
                (x2, y + height / 2 - t / 2),
                (x2, y + height / 2 + t / 2),
                (x2 + t, y + height / 2),
            ],
        }
        tail_points = tails.get(tail, tails["bottom-left"])

        all_x = [body[0], body[2], *[p[0] for p in tail_points]]
        all_y = [body[1], body[3], *[p[1] for p in tail_points]]
        minx, miny = int(min(all_x)), int(min(all_y))
        maxx, maxy = int(math.ceil(max(all_x))), int(math.ceil(max(all_y)))
        bw = maxx - minx
        bh = maxy - miny

        if isinstance(fill, Gradient):
            if bw > 0 and bh > 0:
                mask = PilImage.new("L", (bw, bh), 0)
                mdraw = ImageDraw.Draw(mask)
                mdraw.rounded_rectangle(
                    (body[0] - minx, body[1] - miny, body[2] - minx, body[3] - miny),
                    radius=radius,
                    fill=255,
                )
                mdraw.polygon(
                    [(p[0] - minx, p[1] - miny) for p in tail_points],
                    fill=255,
                )
                grad = fill.render(bw, bh)
                self.image.paste(grad, (minx, miny), mask)
            if outline:
                draw = ImageDraw.Draw(self.image)
                draw.rounded_rectangle(
                    body,
                    radius=radius,
                    outline=outline,
                    width=stroke_width,
                )
                draw.polygon(tail_points, outline=outline, width=stroke_width)
            return self

        layer = PilImage.new("RGBA", self.image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        draw.rounded_rectangle(body, radius=radius, fill=fill)
        draw.polygon(tail_points, fill=fill)
        if outline:
            draw.rounded_rectangle(
                body,
                radius=radius,
                outline=outline,
                width=stroke_width,
            )
            draw.polygon(tail_points, outline=outline, width=stroke_width)
        self._replace(PilImage.alpha_composite(self.image, layer))
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
        fmt = file_format
        if fmt is None and isinstance(fp, (str, Path)):
            ext = Path(fp).suffix.lower().lstrip(".")
            ext_map = {
                "jpg": "JPEG",
                "jpeg": "JPEG",
                "png": "PNG",
                "gif": "GIF",
                "bmp": "BMP",
                "webp": "WEBP",
                "tiff": "TIFF",
                "tif": "TIFF",
            }
            fmt = ext_map.get(ext)

        image = self.image
        if fmt and fmt.upper() in ("JPEG", "JPG") and image.mode == "RGBA":
            background = PilImage.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background

        image.save(fp, fmt, **params)

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
        self._replace(self.image.crop(box))
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
            self._replace(self.image.transpose(PilImage.Transpose.FLIP_LEFT_RIGHT))
        else:
            self._replace(self.image.transpose(PilImage.Transpose.FLIP_TOP_BOTTOM))
        return self

    def invert(self) -> Editor:
        """Invert image colors."""
        # Kept as convert("RGB") -> invert -> convert("RGBA"): the RGB round
        # trip resets alpha to fully opaque, which is the existing behavior;
        # a numpy invert preserving the source alpha would change output.
        self._replace(ImageOps.invert(self.image.convert("RGB")).convert("RGBA"))
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
        self._replace(ImageEnhance.Contrast(self.image).enhance(factor))
        return self

    def brightness(self, factor: float = 1.0) -> Editor:
        """
        Adjust image brightness.

        Parameters
        ----------
        factor : float, optional
            Brightness factor. 1.0 = original, >1 = brighter, <1 = darker.

        """
        self._replace(ImageEnhance.Brightness(self.image).enhance(factor))
        return self

    def saturation(self, factor: float = 1.0) -> Editor:
        """
        Adjust image color saturation.

        Parameters
        ----------
        factor : float, optional
            Saturation factor. 1.0 = original, >1 = more saturated, <1 = less.

        """
        self._replace(ImageEnhance.Color(self.image).enhance(factor))
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
        self._replace(PilImage.alpha_composite(self.image, layer))
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
        self._replace(bg)
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

        drawn = draw.textbbox((x, y), text, font=font)
        self.last_text_bbox = (
            int(drawn[0]),
            int(drawn[1]),
            int(drawn[2]),
            int(drawn[3]),
        )

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

        self._replace(canvas)
        return self

    def effect(
        self,
        effect: Effect,
    ) -> Editor:
        """Apply effect to image. Accepts any Effect subclass instance."""
        self._replace(effect.apply(self.image))
        return self

    def gradient_text(
        self,
        position: tuple[float, float],
        text: str,
        font: ImageFont.FreeTypeFont | Font | None,
        gradient: Gradient,
        *,
        align: Literal["left", "center", "right"] = "left",
        anchor: str | None = None,
        stroke_width: int | None = None,
        stroke_fill: Color = "black",
    ) -> Editor:
        """
        Draw text with glyphs filled by a gradient.

        Parameters
        ----------
        position : tuple[float, float]
            Position to draw text
        text : str
            Text to draw
        font : ImageFont.FreeTypeFont | Font | None
            Font used for text
        gradient : Gradient
            Gradient used to fill the glyphs
        align : Literal["left", "center", "right"], optional
            Align text, by default "left"
        anchor : str, optional
            Pillow text anchor. Overrides align if set.
        stroke_width : int, optional
            Stroke width, by default None
        stroke_fill : Color, optional
            Stroke color, by default "black"

        """
        if isinstance(font, Font):
            font = font.font

        anchors = {"left": "lt", "center": "mt", "right": "rt"}
        effective_anchor = anchor if anchor else anchors[align]

        draw = ImageDraw.Draw(self.image)
        bbox = draw.textbbox(
            position,
            text,
            font=font,
            anchor=effective_anchor,
            stroke_width=stroke_width or 0,
        )
        self.last_text_bbox = (
            int(bbox[0]),
            int(bbox[1]),
            int(bbox[2]),
            int(bbox[3]),
        )
        left, top, right, bottom = self.last_text_bbox
        w = max(right - left, 1)
        h = max(bottom - top, 1)

        if stroke_width:
            draw.text(
                position,
                text,
                fill=stroke_fill,
                font=font,
                anchor=effective_anchor,
                stroke_width=stroke_width,
                stroke_fill=stroke_fill,
            )

        mask = PilImage.new("L", (w, h), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.text(
            (position[0] - left, position[1] - top),
            text,
            fill=255,
            font=font,
            anchor=effective_anchor,
        )
        grad_img = gradient.render(w, h)
        self.image.paste(grad_img, (left, top), mask)

        return self

    def pattern(
        self,
        tile: Image | Editor | Canvas,
        *,
        spacing: tuple[int, int] = (0, 0),
        offset: tuple[int, int] = (0, 0),
    ) -> Editor:
        """
        Tile an image across the whole editor image.

        Parameters
        ----------
        tile : Image | Editor | Canvas
            Tile image to repeat
        spacing : tuple[int, int], optional
            Gap (x, y) between tiles, by default (0, 0)
        offset : tuple[int, int], optional
            Starting offset (x, y), by default (0, 0)

        """
        tile_img = tile.image if isinstance(tile, (Editor, Canvas)) else tile
        tile_img = tile_img.convert("RGBA")
        tw, th = tile_img.size
        step_x = tw + spacing[0]
        step_y = th + spacing[1]
        if step_x <= 0 or th <= 0 or step_y <= 0 or tw <= 0:
            return self

        layer = PilImage.new("RGBA", self.image.size, (0, 0, 0, 0))

        start_x = offset[0]
        while start_x > 0:
            start_x -= step_x
        start_y = offset[1]
        while start_y > 0:
            start_y -= step_y

        y = start_y
        while y < self.image.height:
            x = start_x
            while x < self.image.width:
                layer.paste(tile_img, (x, y), tile_img)
                x += step_x
            y += step_y

        self._replace(PilImage.alpha_composite(self.image, layer))
        layer.close()
        return self

    def copy(self) -> Editor:
        """
        Return a new Editor wrapping a deep copy of this image.

        Returns
        -------
        Editor
            New Editor with an independent copy of the image.

        """
        return Editor(self.image.copy())

    @classmethod
    def from_url(cls, url: str, **kwargs: Any) -> Editor:
        """
        Create an Editor from an image URL.

        Parameters
        ----------
        url : str
            Image URL to load
        **kwargs : Any
            Extra arguments passed to :func:`easy_pil.utils.load_image`

        Returns
        -------
        Editor
            Editor wrapping the downloaded image.

        """
        from .utils import load_image

        image = load_image(url, **kwargs)
        return cls(image)

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
