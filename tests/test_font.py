"""Tests for font."""

import unittest

from PIL import ImageFont

from easy_pil import Font
from easy_pil.font import fonts_path


class TestFont(unittest.TestCase):
    """Tests for the Font class."""

    def test_init(self) -> None:
        """Tests Font constructor with path."""
        f = Font(fonts_path["poppins"]["regular"], size=20)
        self.assertIsInstance(f, Font)
        self.assertIsInstance(f.font, ImageFont.FreeTypeFont)

    def test_getsize(self) -> None:
        """Tests Font.getsize."""
        f = Font(fonts_path["poppins"]["regular"], size=20)
        w, h = f.getsize("Hello")
        self.assertIsInstance(w, (int, float))
        self.assertIsInstance(h, (int, float))

    def test_poppins_regular(self) -> None:
        """Tests Font.poppins regular."""
        f = Font.poppins(size=20)
        self.assertIsInstance(f, ImageFont.FreeTypeFont)

    def test_poppins_bold(self) -> None:
        """Tests Font.poppins bold."""
        f = Font.poppins(variant="bold", size=20)
        self.assertIsInstance(f, ImageFont.FreeTypeFont)

    def test_poppins_italic(self) -> None:
        """Tests Font.poppins italic."""
        f = Font.poppins(variant="italic", size=20)
        self.assertIsInstance(f, ImageFont.FreeTypeFont)

    def test_caveat_regular(self) -> None:
        """Tests Font.caveat."""
        f = Font.caveat(size=20)
        self.assertIsInstance(f, ImageFont.FreeTypeFont)

    def test_montserrat_regular(self) -> None:
        """Tests Font.montserrat."""
        f = Font.montserrat(size=20)
        self.assertIsInstance(f, ImageFont.FreeTypeFont)

    def test_montserrat_bold(self) -> None:
        """Tests Font.montserrat bold."""
        f = Font.montserrat(variant="bold", size=20)
        self.assertIsInstance(f, ImageFont.FreeTypeFont)


if __name__ == "__main__":
    unittest.main()
