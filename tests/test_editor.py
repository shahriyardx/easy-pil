"""Tests for editor."""

import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from easy_pil import Canvas, Editor, Font, Text


class TestEditor(unittest.TestCase):
    """Tests for the Editor class."""

    def setUp(self) -> None:
        self.canvas = Canvas((100, 100), color="black")
        self.editor = Editor(self.canvas)

    def test_from_canvas(self) -> None:
        """Tests editor from canvas."""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas)
        assert isinstance(editor, Editor)

    def test_from_path(self) -> None:
        """Tests editor from path."""
        editor = Editor(
            Path.cwd() / "examples" / "assets" / "pfp.png",
        )
        assert isinstance(editor, Editor)

    def test_from_image(self) -> None:
        """Tests editor from image."""
        image = Image.open(
            Path.cwd() / "examples" / "assets" / "pfp.png",
        )
        editor = Editor(image)
        assert isinstance(editor, Editor)

    def test_from_editor(self) -> None:
        """Tests editor from canvas."""
        canvas = Canvas((100, 100), color="black")
        editor1 = Editor(canvas)
        editor2 = Editor(editor1)
        assert type(editor1) is type(editor2)

    def test_from_bytes(self) -> None:
        """Tests editor from raw bytes."""
        canvas = Canvas((50, 50), color="red")
        buf = Editor(canvas).to_bytes()
        editor = Editor(buf)
        assert isinstance(editor, Editor)

    def test_text(self) -> None:
        """Tests editor text."""
        editor = self.editor.text(
            (50, 50),
            "Hello World",
            color="white",
            font=Font.poppins(size=20),
        )
        assert isinstance(editor, Editor)

    def test_text_no_font(self) -> None:
        """Tests editor text with default font."""
        editor = self.editor.text((10, 10), "Test")
        assert isinstance(editor, Editor)

    def test_text_with_stroke(self) -> None:
        """Tests editor text with stroke."""
        editor = self.editor.text(
            (50, 50), "Stroke", color="white",
            stroke_width=2, stroke_fill="black",
        )
        assert isinstance(editor, Editor)

    def test_text_align_right(self) -> None:
        """Tests editor text right-aligned."""
        editor = self.editor.text(
            (90, 50), "Right", color="white", align="right",
        )
        assert isinstance(editor, Editor)

    def test_text_align_center(self) -> None:
        """Tests editor text center-aligned."""
        editor = self.editor.text(
            (50, 50), "Center", color="white", align="center",
        )
        assert isinstance(editor, Editor)

    def test_text_with_font_object(self) -> None:
        """Tests editor text with Font object."""
        font = Font.poppins(size=20)
        editor = self.editor.text((10, 10), "Hi", font=font)
        assert isinstance(editor, Editor)

    def test_rich_text(self) -> None:
        """Tests rich_text with mixed styles."""
        hello = Text("Hello ", color="white", font=Font.poppins(size=20))
        world = Text("World", color="red", font=Font.poppins(size=20))
        editor = self.editor.rich_text(
            (0, 0), [hello, world],
            space_separated=False, align="left",
        )
        assert isinstance(editor, Editor)

    def test_rich_text_right(self) -> None:
        """Tests rich_text right-aligned."""
        t = Text("Hi", color="white", font=Font.poppins(size=20))
        editor = self.editor.rich_text((90, 0), [t], align="right")
        assert isinstance(editor, Editor)

    def test_rich_text_center(self) -> None:
        """Tests rich_text center-aligned."""
        t = Text("Hi", color="white", font=Font.poppins(size=20))
        editor = self.editor.rich_text((50, 0), [t], align="center")
        assert isinstance(editor, Editor)

    def test_multi_text_alias(self) -> None:
        """Tests multi_text backward-compat alias."""
        t = Text("Hi", color="white", font=Font.poppins(size=20))
        editor = self.editor.multi_text((0, 0), [t])
        assert isinstance(editor, Editor)

    def test_text_box(self) -> None:
        """Tests text_box auto-wrapping."""
        editor = self.editor.text_box(
            (10, 10),
            "This is a long text that should wrap",
            Font.poppins(size=16),
            color="white",
            max_width=60,
        )
        assert isinstance(editor, Editor)

    def test_text_box_align_center(self) -> None:
        """Tests text_box centered."""
        editor = self.editor.text_box(
            (50, 10), "A B C", Font.poppins(size=16),
            max_width=80, align="center",
        )
        assert isinstance(editor, Editor)

    def test_text_box_align_right(self) -> None:
        """Tests text_box right-aligned."""
        editor = self.editor.text_box(
            (90, 10), "A B C", Font.poppins(size=16),
            max_width=80, align="right",
        )
        assert isinstance(editor, Editor)

    def test_text_box_stroke(self) -> None:
        """Tests text_box with stroke."""
        editor = self.editor.text_box(
            (10, 10), "Text", Font.poppins(size=16),
            stroke_width=1, stroke_fill="black",
        )
        assert isinstance(editor, Editor)

    def test_text_box_no_max_width(self) -> None:
        """Tests text_box defaults to image width."""
        editor = self.editor.text_box(
            (10, 10), "Short", Font.poppins(size=16),
        )
        assert isinstance(editor, Editor)

    def test_text_box_font_object(self) -> None:
        """Tests text_box with Font object."""
        font = Font.poppins(size=16)
        editor = self.editor.text_box((10, 10), "Hi", font)
        assert isinstance(editor, Editor)

    def test_text_shadow(self) -> None:
        """Tests text_shadow."""
        editor = self.editor.text_shadow(
            (50, 50), "Shadow", Font.poppins(size=20),
            color="white", shadow_color="black",
        )
        assert isinstance(editor, Editor)

    def test_text_shadow_default_font(self) -> None:
        """Tests text_shadow with no font."""
        editor = self.editor.text_shadow((50, 50), "Shadow")
        assert isinstance(editor, Editor)

    def test_text_shadow_stroke(self) -> None:
        """Tests text_shadow with stroke."""
        editor = self.editor.text_shadow(
            (50, 50), "Stroke", Font.poppins(size=20),
            stroke_width=1,
        )
        assert isinstance(editor, Editor)

    def test_centered_text(self) -> None:
        """Tests centered_text."""
        editor = self.editor.centered_text(
            "Center", Font.poppins(size=20),
        )
        assert isinstance(editor, Editor)

    def test_centered_text_color(self) -> None:
        """Tests centered_text with color."""
        editor = self.editor.centered_text(
            "Red", Font.poppins(size=20), color="red",
        )
        assert isinstance(editor, Editor)

    def test_fit_text(self) -> None:
        """Tests fit_text returns a font that fits."""
        font_path = Font.poppins(size=20).path
        font = self.editor.fit_text("Hello", max_width=80, font_path=font_path)
        assert font is not None

    def test_fit_text_min_size(self) -> None:
        """Tests fit_text with min_size."""
        font_path = Font.poppins(size=20).path
        font = self.editor.fit_text(
            "Very Long Text Here", max_width=30,
            font_path=font_path, max_size=20, min_size=5,
        )
        assert font is not None

    def test_circle(self) -> None:
        """Tests editor circle."""
        editor = self.editor.circle_image()
        assert isinstance(editor, Editor)

    def test_rounded_corners(self) -> None:
        """Tests editor rounded corners."""
        editor = self.editor.rounded_corners(radius=10, offset=5)
        assert isinstance(editor, Editor)

    def test_resize(self) -> None:
        """Tests editor resize."""
        editor = self.editor.resize((100, 50), crop=True)
        assert isinstance(editor, Editor)

    def test_resize_no_crop(self) -> None:
        """Tests editor resize without crop."""
        editor = self.editor.resize((50, 50))
        assert isinstance(editor, Editor)

    def test_rotate(self) -> None:
        """Tests editor rotate."""
        editor = self.editor.rotate(45)
        assert isinstance(editor, Editor)

    def test_rotate_expand(self) -> None:
        """Tests editor rotate with expand."""
        editor = self.editor.rotate(45, expand=True)
        assert isinstance(editor, Editor)

    def test_blur_gaussian(self) -> None:
        """Tests editor gaussian blur."""
        editor = self.editor.blur(mode="gaussian", amount=5)
        assert isinstance(editor, Editor)

    def test_blur_box(self) -> None:
        """Tests editor box blur."""
        editor = self.editor.blur(mode="box", amount=5)
        assert isinstance(editor, Editor)

    def test_blend(self) -> None:
        """Tests editor blend."""
        canvas2 = Canvas((100, 100), color="red")
        editor = self.editor.blend(canvas2, alpha=1, on_top=True)
        assert isinstance(editor, Editor)

    def test_blend_no_on_top(self) -> None:
        """Tests editor blend without on_top."""
        canvas2 = Canvas((100, 100), color="red")
        editor = self.editor.blend(canvas2, alpha=0.5)
        assert isinstance(editor, Editor)

    def test_blend_different_size(self) -> None:
        """Tests editor blend with different-sized image."""
        small = Canvas((50, 50), color="red")
        editor = self.editor.blend(small, alpha=0.5)
        assert isinstance(editor, Editor)

    def test_paste(self) -> None:
        """Tests editor paste."""
        canvas2 = Canvas((50, 50), color="red")
        editor = self.editor.paste(canvas2, (0, 0))
        assert isinstance(editor, Editor)

    def test_ellipse(self) -> None:
        """Tests editor ellipse."""
        editor = self.editor.ellipse((50, 50), 80, 60, fill="red")
        assert isinstance(editor, Editor)

    def test_ellipse_outline(self) -> None:
        """Tests editor ellipse with outline."""
        editor = self.editor.ellipse(
            (50, 50), 80, 60, fill="red",
            outline="white", stroke_width=3,
        )
        assert isinstance(editor, Editor)

    def test_bar(self) -> None:
        """Tests editor bar."""
        editor = self.editor.bar(
            (10, 10), 80, 10, 50,
            color="white", outline="black",
            stroke_width=2, radius=5,
        )
        assert isinstance(editor, Editor)

    def test_rounded_bar(self) -> None:
        """Tests editor rounded bar."""
        editor = self.editor.rounded_bar(
            (10, 10), 80, 80, 50,
            color="white", stroke_width=2,
        )
        assert isinstance(editor, Editor)

    def test_arc(self) -> None:
        """Tests editor arc."""
        editor = self.editor.arc(
            (10, 10), 80, 80, 0, 90,
            color="white", stroke_width=2,
        )
        assert isinstance(editor, Editor)

    def test_polygon(self) -> None:
        """Tests editor polygon."""
        cords = [(10, 10), (90, 10), (90, 90), (10, 90)]
        editor = self.editor.polygon(cords, color="white", outline="black")
        assert isinstance(editor, Editor)

    def test_polygon_fill_only(self) -> None:
        """Tests editor polygon with fill only."""
        editor = self.editor.polygon([(10, 10), (50, 10), (30, 50)], color="red")
        assert isinstance(editor, Editor)

    def test_line(self) -> None:
        """Tests editor line."""
        editor = self.editor.line((10, 10), (90, 90), width=3, fill="white")
        assert isinstance(editor, Editor)

    def test_donut(self) -> None:
        """Tests editor donut."""
        editor = self.editor.donut(
            (50, 50), inner_radius=15, outer_radius=30, fill="teal",
        )
        assert isinstance(editor, Editor)

    def test_invert(self) -> None:
        """Tests editor invert."""
        editor = self.editor.invert()
        assert isinstance(editor, Editor)

    def test_contrast(self) -> None:
        """Tests editor contrast."""
        editor = self.editor.contrast(1.5)
        assert isinstance(editor, Editor)

    def test_brightness(self) -> None:
        """Tests editor brightness."""
        editor = self.editor.brightness(1.2)
        assert isinstance(editor, Editor)

    def test_saturation(self) -> None:
        """Tests editor saturation."""
        editor = self.editor.saturation(0.8)
        assert isinstance(editor, Editor)

    def test_crop(self) -> None:
        """Tests editor crop."""
        editor = self.editor.crop((10, 10, 50, 50))
        assert isinstance(editor, Editor)
        self.assertEqual(editor.image.size, (40, 40))

    def test_flip_horizontal(self) -> None:
        """Tests editor horizontal flip."""
        editor = self.editor.flip(horizontal=True)
        assert isinstance(editor, Editor)

    def test_flip_vertical(self) -> None:
        """Tests editor vertical flip."""
        editor = self.editor.flip()
        assert isinstance(editor, Editor)

    def test_thumbnail(self) -> None:
        """Tests editor thumbnail."""
        editor = self.editor.thumbnail((50, 50))
        assert isinstance(editor, Editor)

    def test_open(self) -> None:
        """Tests editor open class method."""
        path = Path.cwd() / "examples" / "assets" / "pfp.png"
        editor = Editor.open(path)
        assert isinstance(editor, Editor)

    def test_to_bytes(self) -> None:
        """Tests editor to_bytes."""
        data = self.editor.to_bytes()
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_to_bytes_jpeg(self) -> None:
        """Tests editor to_bytes with JPEG format."""
        img = Image.new("RGB", (100, 100), "white")
        editor = Editor(img)
        data = editor.to_bytes(fmt="JPEG")
        assert isinstance(data, bytes)

    def test_bytes(self) -> None:
        """Tests editor image_bytes property."""
        buf = self.editor.image_bytes
        assert isinstance(buf, BytesIO)

    def test_compose_vertical(self) -> None:
        """Tests compose vertical."""
        c1 = Canvas((50, 50), color="red")
        c2 = Canvas((50, 50), color="blue")
        editor = self.editor.compose(
            [Editor(c1), Editor(c2)],
            direction="vertical", align="center",
        )
        assert isinstance(editor, Editor)

    def test_compose_horizontal(self) -> None:
        """Tests compose horizontal."""
        c1 = Canvas((50, 50), color="red")
        c2 = Canvas((50, 50), color="blue")
        editor = self.editor.compose(
            [Editor(c1), Editor(c2)],
            direction="horizontal", align="center",
        )
        assert isinstance(editor, Editor)

    def test_add_border(self) -> None:
        """Tests add_border."""
        editor = self.editor.add_border(width=5, color="red")
        assert isinstance(editor, Editor)
        # border adds 2*width to each dimension
        self.assertEqual(editor.image.size, (110, 110))

    def test_mask(self) -> None:
        """Tests mask with Editor mask."""
        mask_source = Canvas((100, 100), color="white")
        mask_editor = Editor(mask_source).ellipse((50, 50), 60, 60, fill="white")
        editor = self.editor.mask(mask_editor)
        assert isinstance(editor, Editor)

    def test_mask_inverted(self) -> None:
        """Tests mask with invert."""
        mask_source = Canvas((100, 100), color="white")
        mask_img = Editor(mask_source).ellipse((50, 50), 60, 60, fill="white")
        editor = self.editor.mask(mask_img, invert=True)
        assert isinstance(editor, Editor)

    def test_mask_with_pil_image(self) -> None:
        """Tests mask with raw PIL Image."""
        mask = Image.new("L", (100, 100), 255)
        editor = self.editor.mask(mask)
        assert isinstance(editor, Editor)

    def test_save(self) -> None:
        """Tests editor save."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png") as f:
            self.editor.save(f.name)
            saved = Image.open(f.name)
            self.assertEqual(saved.size, (100, 100))

    def test_show(self) -> None:
        """Tests editor show (just verify it exists)."""
        assert hasattr(self.editor, "show")
        assert callable(self.editor.show)

    def test_close(self) -> None:
        """Tests editor close."""
        self.editor.close()  # should not raise


if __name__ == "__main__":
    unittest.main()
