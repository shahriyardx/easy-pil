import unittest

from easy_pil import Canvas


class TestCanvas(unittest.TestCase):
    def test_canvas(self):
        """Tests canvas"""
        canvas = Canvas((100, 100), color="black")
        canvas2 = Canvas(width=100, height=100, color="black")
        self.assertEqual(canvas.size, (100, 100))
        self.assertEqual(canvas2.size, (100, 100))


if __name__ == "__main__":
    unittest.main()
