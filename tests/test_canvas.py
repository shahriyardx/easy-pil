"""Tests for canvas."""

import unittest

from easy_pil import Canvas


class TestCanvas(unittest.TestCase):
    """Tests for the Canvas class."""

    def test_canvas(self) -> None:
        """Tests canvas."""
        canvas = Canvas((100, 100), color="black")
        canvas2 = Canvas(width=100, height=100, color="black")
        assert canvas.size == (100, 100)
        assert canvas2.size == (100, 100)

    def test_canvas_no_size(self) -> None:
        """Tests canvas ValueError when no size provided."""
        with self.assertRaises(ValueError):
            Canvas()


if __name__ == "__main__":
    unittest.main()
