import os
import unittest
from io import BytesIO

from PIL import Image

from easy_pil import Canvas, Editor, Font, Text


class TestEditor(unittest.TestCase):
    def test_from_canvas(self):
        """Tests editor from canvas"""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas)
        self.assertIsInstance(editor, Editor)

    def test_from_path(self):
        """Tests editor from path"""
        editor = Editor(os.path.join(os.getcwd(), "examples", "assets", "pfp.png"))
        self.assertIsInstance(editor, Editor)

    def test_from_image(self):
        """Tests editor from image"""
        image = Image.open(os.path.join(os.getcwd(), "examples", "assets", "pfp.png"))
        editor = Editor(image)
        self.assertIsInstance(editor, Editor)

    def test_from_editor(self):
        """Tests editor from canvas"""
        canvas = Canvas((100, 100), color="black")
        editor1 = Editor(canvas)
        editor2 = Editor(editor1)
        self.assertEqual(type(editor1), type(editor2))

    def test_text(self):
        """Tests editor text"""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).text((50, 50), "Hello World", color="white", font=Font.poppins(size=20))
        self.assertIsInstance(editor, Editor)

    def test_circle(self):
        """Tests editor circle"""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).circle_image()
        self.assertIsInstance(editor, Editor)

    def test_rounded_corners(self):
        """Tests editor rounded corners"""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).rounded_corners(radius=10, offset=5)
        self.assertIsInstance(editor, Editor)

    def test_resize(self):
        """Tests editor resize"""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).resize((100, 50), crop=True)
        self.assertIsInstance(editor, Editor)

    def test_rotate(self):
        """Tests editor rotate"""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).rotate(45)
        self.assertIsInstance(editor, Editor)

    def test_blur(self):
        """Tests editor blur"""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).blur(mode="gaussian", amount=10)
        self.assertIsInstance(editor, Editor)

    def test_blend(self):
        """Tests editor blend"""
        canvas = Canvas((100, 100), color="black")
        canvas2 = Canvas((100, 100), color="red")
        editor = Editor(canvas).blend(canvas2, alpha=1, on_top=True)
        self.assertIsInstance(editor, Editor)

    def test_paste(self):
        """Tests editor paste"""
        canvas = Canvas((100, 100), color="black")
        canvas2 = Canvas((50, 50), color="red")
        editor = Editor(canvas).paste(canvas2, (0, 0))
        self.assertIsInstance(editor, Editor)

    def test_multi_text(self):
        """Tests editor multi text"""
        canvas = Canvas((200, 100), color="black")
        hello = Text("Hello ", color="white", font=Font.poppins(size=20))
        world = Text("World", color="white", font=Font.poppins(size=20))
        editor = Editor(canvas).multi_text((0, 0), [hello, world], space_separated=False, align="left")
        self.assertIsInstance(editor, Editor)

    def test_rectangle(self):
        """Tests editor rectangle"""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).rectangle((10, 10), 80, 10, color="white")
        self.assertIsInstance(editor, Editor)

    def test_bar(self):
        """Tests editor bar"""
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
        self.assertIsInstance(editor, Editor)

    def test_rounded_bar(self):
        """Tests editor rounded bar"""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).rounded_bar((10, 10), 80, 80, 50, color="white", stroke_width=2)
        self.assertIsInstance(editor, Editor)

    def test_arc(self):
        """Tests editor arc"""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).arc((10, 10), 80, 80, 0, 90, color="white", stroke_width=2)
        self.assertIsInstance(editor, Editor)

    def test_polygon(self):
        """Tests editor polygon"""
        canvas = Canvas((100, 100), color="black")
        cords = [(10, 10), (90, 10), (90, 90), (10, 90)]
        editor = Editor(canvas).polygon(cords, color="white", outline="black")
        self.assertIsInstance(editor, Editor)

    def test_bytes(self):
        """Tests editor bytes"""
        canvas = Canvas((100, 100), color="black")
        editor = Editor(canvas).image_bytes
        self.assertIsInstance(editor, BytesIO)


if __name__ == "__main__":
    unittest.main()
