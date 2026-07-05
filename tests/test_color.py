"""Tests for the unified color normalization helpers."""

import unittest

from PIL import Image as PilImage

from easy_pil import to_rgb, to_rgba
from easy_pil.effect import EdgeGlow, Gradient


class TestToRgba(unittest.TestCase):
    """Tests for easy_pil.color.to_rgba."""

    def test_string_named(self) -> None:
        self.assertEqual(to_rgba("red"), (255, 0, 0, 255))

    def test_string_with_custom_alpha(self) -> None:
        self.assertEqual(to_rgba("red", alpha=128), (255, 0, 0, 128))

    def test_hex_int(self) -> None:
        self.assertEqual(to_rgba(0xFF0000), (255, 0, 0, 255))
        self.assertEqual(to_rgba(0x00FF00), (0, 255, 0, 255))
        self.assertEqual(to_rgba(0x0000FF), (0, 0, 255, 255))

    def test_int_with_custom_alpha(self) -> None:
        self.assertEqual(to_rgba(0xFF0000, alpha=64), (255, 0, 0, 64))

    def test_rgb_tuple(self) -> None:
        self.assertEqual(to_rgba((10, 20, 30)), (10, 20, 30, 255))

    def test_rgb_tuple_custom_alpha(self) -> None:
        self.assertEqual(to_rgba((10, 20, 30), alpha=100), (10, 20, 30, 100))

    def test_rgba_tuple_preserves_alpha(self) -> None:
        # Explicit 4-tuple alpha wins over the alpha kwarg.
        self.assertEqual(to_rgba((10, 20, 30, 40)), (10, 20, 30, 40))
        self.assertEqual(to_rgba((10, 20, 30, 40), alpha=99), (10, 20, 30, 40))

    def test_clamping(self) -> None:
        self.assertEqual(to_rgba((-5, 300, 128, 999)), (0, 255, 128, 255))
        self.assertEqual(to_rgba((0, 0, 0), alpha=1000), (0, 0, 0, 255))
        self.assertEqual(to_rgba((0, 0, 0), alpha=-10), (0, 0, 0, 0))


class TestToRgb(unittest.TestCase):
    """Tests for easy_pil.color.to_rgb."""

    def test_string_named(self) -> None:
        self.assertEqual(to_rgb("red"), (255, 0, 0))

    def test_hex_int(self) -> None:
        self.assertEqual(to_rgb(0xFF0000), (255, 0, 0))

    def test_rgb_tuple(self) -> None:
        self.assertEqual(to_rgb((10, 20, 30)), (10, 20, 30))

    def test_rgba_tuple_drops_alpha(self) -> None:
        self.assertEqual(to_rgb((10, 20, 30, 40)), (10, 20, 30))

    def test_clamping(self) -> None:
        self.assertEqual(to_rgb((-5, 300, 128)), (0, 255, 128))


class TestColorRegressions(unittest.TestCase):
    """Regression tests for previously-fixed effect color behavior."""

    def test_edge_glow_string_honored_not_cyan(self) -> None:
        # EdgeGlow must resolve string colors via getrgb, not fall back to cyan.
        glow = EdgeGlow(color="red")
        c = to_rgb(glow.color)
        self.assertEqual(c, (255, 0, 0))

    def test_gradient_visible_and_colored(self) -> None:
        # Gradient over an opaque image should produce a visible, colored
        # result: red-ish on the left, blue-ish on the right.
        base = PilImage.new("RGBA", (64, 32), (0, 0, 0, 255))
        result = Gradient(colors=["red", "blue"]).apply(base)

        left = result.getpixel((0, 16))
        right = result.getpixel((63, 16))

        # Opaque output (source alpha preserved).
        self.assertEqual(left[3], 255)
        self.assertEqual(right[3], 255)

        # Left leans red, right leans blue.
        self.assertGreater(left[0], left[2])
        self.assertGreater(right[2], right[0])


if __name__ == "__main__":
    unittest.main()
