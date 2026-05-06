"""Tests for editor."""

import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from easy_pil import Canvas, Editor, Font, Text


class TestEditor(unittest.TestCase):
    """Tests for the Editor class."""

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

    def test_text(self) -> None:
        """Tests editor text."""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).text(
            (50, 50),
            "Hello World",
            color="white",
            font=Font.poppins(size=20),
        )
        assert isinstance(editor, Editor)

    def test_circle(self) -> None:
        """Tests editor circle."""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).circle_image()
        assert isinstance(editor, Editor)

    def test_rounded_corners(self) -> None:
        """Tests editor rounded corners."""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).rounded_corners(radius=10, offset=5)
        assert isinstance(editor, Editor)

    def test_resize(self) -> None:
        """Tests editor resize."""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).resize((100, 50), crop=True)
        assert isinstance(editor, Editor)

    def test_rotate(self) -> None:
        """Tests editor rotate."""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).rotate(45)
        assert isinstance(editor, Editor)

    def test_blur(self) -> None:
        """Tests editor blur."""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).blur(mode="gaussian", amount=10)
        assert isinstance(editor, Editor)

    def test_blend(self) -> None:
        """Tests editor blend."""
        canvas = Canvas((100, 100), color="black")
        canvas2 = Canvas((100, 100), color="red")
        editor = Editor(canvas).blend(canvas2, alpha=1, on_top=True)
        assert isinstance(editor, Editor)

    def test_paste(self) -> None:
        """Tests editor paste."""
        canvas = Canvas((100, 100), color="black")
        canvas2 = Canvas((50, 50), color="red")
        editor = Editor(canvas).paste(canvas2, (0, 0))
        assert isinstance(editor, Editor)

    def test_multi_text(self) -> None:
        """Tests editor multi text."""
        canvas = Canvas((200, 100), color="black")
        hello = Text("Hello ", color="white", font=Font.poppins(size=20))
        world = Text("World", color="white", font=Font.poppins(size=20))
        editor = Editor(canvas).multi_text(
            (0, 0),
            [hello, world],
            space_separated=False,
            align="left",
        )
        assert isinstance(editor, Editor)

    def test_rectangle(self) -> None:
        """Tests editor rectangle."""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).rectangle((10, 10), 80, 10, color="white")
        assert isinstance(editor, Editor)

    def test_bar(self) -> None:
        """Tests editor bar."""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).bar(
            (10, 10),
            80,
            10,
            50,
            color="white",
            outline="black",
            stroke_width=2,
            radius=5,
        )
        assert isinstance(editor, Editor)

    def test_rounded_bar(self) -> None:
        """Tests editor rounded bar."""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).rounded_bar(
            (10, 10),
            80,
            80,
            50,
            color="white",
            stroke_width=2,
        )
        assert isinstance(editor, Editor)

    def test_arc(self) -> None:
        """Tests editor arc."""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).arc(
            (10, 10),
            80,
            80,
            0,
            90,
            color="white",
            stroke_width=2,
        )
        assert isinstance(editor, Editor)

    def test_polygon(self) -> None:
        """Tests editor polygon."""
        canvas = Canvas((100, 100), color="black")
        cords = [(10, 10), (90, 10), (90, 90), (10, 90)]
        editor = Editor(canvas).polygon(cords, color="white", outline="black")
        assert isinstance(editor, Editor)

    def test_bytes(self) -> None:
        """Tests editor bytes."""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).image_bytes
        assert isinstance(editor, BytesIO)


if __name__ == "__main__":
    unittest.main()
