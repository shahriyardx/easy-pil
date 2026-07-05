"""Tests for font."""

import unittest

from PIL import Image, ImageDraw, ImageFont

from easy_pil import Font
from easy_pil.font import draw_text_with_fallback, fonts_path


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

    def test_load(self) -> None:
        """Tests Font.load convenience constructor."""
        f = Font.load(fonts_path["poppins"]["regular"], size=32)
        self.assertIsInstance(f, Font)
        self.assertIsInstance(f.font, ImageFont.FreeTypeFont)
        self.assertEqual(f.font.size, 32)

    def test_can_render_present(self) -> None:
        """Tests can_render returns True for present glyphs and space."""
        f = Font(fonts_path["poppins"]["regular"], size=20)
        self.assertTrue(f.can_render("A"))
        self.assertTrue(f.can_render(" "))

    def test_can_render_missing(self) -> None:
        """Tests can_render returns False for a glyph the font lacks."""
        f = Font(fonts_path["poppins"]["regular"], size=20)
        # Pick a glyph the Latin font actually lacks, verifying as we go.
        missing = None
        for candidate in ("😀", "漢"):
            if not f.can_render(candidate):
                missing = candidate
                break
        self.assertIsNotNone(missing, "expected the Latin font to lack a glyph")
        self.assertFalse(f.can_render(missing))


class TestDrawTextWithFallback(unittest.TestCase):
    """Tests for draw_text_with_fallback."""

    def test_single_font_matches_normal_draw(self) -> None:
        """A single font draws identically to a plain ImageDraw.text call."""
        font = Font.poppins(size=24)
        text = "Hello"
        position = (5, 7)

        ref_img = Image.new("RGBA", (200, 60), (0, 0, 0, 0))
        ref_draw = ImageDraw.Draw(ref_img)
        ref_draw.text(position, text, font=font, fill="white")
        ref_bbox = ref_draw.textbbox(position, text, font=font)

        fb_img = Image.new("RGBA", (200, 60), (0, 0, 0, 0))
        fb_draw = ImageDraw.Draw(fb_img)
        fb_bbox = draw_text_with_fallback(fb_draw, position, text, [font], fill="white")

        self.assertEqual(fb_bbox, ref_bbox)
        self.assertEqual(fb_img.tobytes(), ref_img.tobytes())
        # Plausible, non-degenerate bbox.
        self.assertLess(fb_bbox[0], fb_bbox[2])
        self.assertLess(fb_bbox[1], fb_bbox[3])

    def test_run_split_across_two_fonts(self) -> None:
        """Text splits into runs when the primary font lacks a glyph."""
        # Caveat lacks GREEK SMALL LETTER PI while Poppins provides it.
        caveat = Font.caveat(size=24)
        poppins = Font.poppins(size=24)
        self.assertFalse(Font(fonts_path["caveat"]["regular"]).can_render("π"))
        self.assertTrue(Font(fonts_path["poppins"]["regular"]).can_render("π"))

        text = "aπb"
        position = (4, 6)
        img = Image.new("RGBA", (200, 60), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        bbox = draw_text_with_fallback(
            draw, position, text, [caveat, poppins], fill="white"
        )

        self.assertEqual(len(bbox), 4)
        self.assertTrue(all(isinstance(v, int) for v in bbox))
        # Bbox covers the full drawn string width.
        self.assertLess(bbox[0], bbox[2])
        self.assertLess(bbox[1], bbox[3])
        # Something was actually rendered onto the canvas.
        self.assertIsNotNone(img.getbbox())


if __name__ == "__main__":
    unittest.main()
