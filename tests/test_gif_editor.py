"""Tests for gif_editor."""

import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from easy_pil import Editor
from easy_pil.gif_editor import GifEditor


def _make_gif_bytes() -> bytes:
    """Create a simple 2-frame GIF in memory."""
    frames = [
        Image.new("RGBA", (10, 10), (255, 0, 0, 255)),
        Image.new("RGBA", (10, 10), (0, 0, 255, 255)),
    ]
    buf = BytesIO()
    frames[0].save(buf, "GIF", save_all=True, append_images=frames[1:])
    buf.seek(0)
    return buf.getvalue()


class TestGifEditor(unittest.TestCase):
    """Tests for the GifEditor class."""

    def setUp(self) -> None:
        self.gif_bytes = _make_gif_bytes()
        self.gif_image = Image.open(BytesIO(self.gif_bytes))

    def test_from_bytesio(self) -> None:
        """Tests GifEditor from BytesIO."""
        gif = GifEditor(BytesIO(self.gif_bytes))
        self.assertIsInstance(gif, GifEditor)
        self.assertEqual(gif.size, (10, 10))
        self.assertEqual(len(gif.frames), 2)

    def test_from_pil_image(self) -> None:
        """Tests GifEditor from GifImageFile."""
        gif = GifEditor(self.gif_image)
        self.assertIsInstance(gif, GifEditor)
        self.assertEqual(gif.size, (10, 10))

    def test_apply_to_frames(self) -> None:
        """Tests applying operation to all frames via __getattr__."""
        gif = GifEditor(BytesIO(self.gif_bytes))
        gif.invert()
        for frame in gif.frames:
            self.assertIsInstance(frame, Editor)

    def test_image_bytes(self) -> None:
        """Tests image_bytes property."""
        gif = GifEditor(BytesIO(self.gif_bytes))
        buf = gif.image_bytes
        self.assertIsInstance(buf, BytesIO)
        data = buf.read()
        self.assertTrue(len(data) > 0)

    def test_save_path(self) -> None:
        """Tests save to file path."""
        gif = GifEditor(BytesIO(self.gif_bytes))
        with tempfile.NamedTemporaryFile(suffix=".gif") as f:
            gif.save(f.name)
            saved = Image.open(f.name)
            self.assertEqual(saved.size, (10, 10))

    def test_save_bytesio(self) -> None:
        """Tests save to BytesIO."""
        gif = GifEditor(BytesIO(self.gif_bytes))
        buf = BytesIO()
        gif.save(buf)
        buf.seek(0)
        data = buf.read()
        self.assertTrue(len(data) > 0)

    def test_from_path(self) -> None:
        """Tests GifEditor from file path (save then reopen)."""
        with tempfile.NamedTemporaryFile(suffix=".gif") as f:
            f.write(self.gif_bytes)
            f.flush()
            gif = GifEditor(Path(f.name))
            self.assertIsInstance(gif, GifEditor)
            self.assertEqual(gif.size, (10, 10))

    def test_close_frames(self) -> None:
        """Tests that all frames can be closed."""
        gif = GifEditor(BytesIO(self.gif_bytes))
        for frame in gif.frames:
            frame.close()


if __name__ == "__main__":
    unittest.main()
