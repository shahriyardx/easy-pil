"""Tests for text."""

import unittest

from easy_pil import Font, Text
from easy_pil.font import fonts_path


class TestText(unittest.TestCase):
    """Tests for the Text class."""

    def test_with_font_instance(self) -> None:
        """Tests Text with Font instance (not FreeTypeFont)."""
        f = Font(fonts_path["poppins"]["regular"], size=20)
        t = Text("Hello", font=f, color="white")
        self.assertIsInstance(t, Text)

    def test_with_freetype_font(self) -> None:
        """Tests Text with FreeTypeFont directly."""
        font = Font.poppins(size=20)
        t = Text("Hello", font=font, color="white")
        self.assertIsInstance(t, Text)

    def test_getsize(self) -> None:
        """Tests Text.getsize."""
        font = Font.poppins(size=20)
        t = Text("Hello", font=font, color="white")
        w, h = t.getsize()
        self.assertIsInstance(w, (int, float))
        self.assertIsInstance(h, (int, float))


if __name__ == "__main__":
    unittest.main()
