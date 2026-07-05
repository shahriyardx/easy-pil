"""Tests for aio_editor."""

import unittest
from io import BytesIO

from PIL import Image

from easy_pil import AioEditor, Canvas, Editor


class TestAioEditor(unittest.IsolatedAsyncioTestCase):
    """Tests for the AioEditor class."""

    def setUp(self) -> None:
        self.canvas = Canvas((50, 50), color="black")
        self.aio = AioEditor(self.canvas)

    async def test_execute_empty(self) -> None:
        """Test execute with no instructions."""
        editor = await self.aio.execute()
        self.assertIsInstance(editor, Editor)

    async def test_execute_with_text(self) -> None:
        """Test execute with a queued instruction."""
        from easy_pil import Font

        self.aio.text((10, 10), "Hi", font=Font.poppins(size=20), color="white")
        editor = await self.aio.execute()
        self.assertIsInstance(editor, Editor)

    async def test_execute_multiple(self) -> None:
        """Test execute chained instructions."""
        self.aio.rectangle((5, 5), 20, 20, fill="red")
        self.aio.ellipse((25, 25), 10, 10, fill="blue")
        editor = await self.aio.execute()
        self.assertIsInstance(editor, Editor)

    def test_getattr_invalid(self) -> None:
        """Test __getattr__ with non-existent method."""
        with self.assertRaises(AttributeError):
            _ = self.aio.nonexistent_method  # type: ignore[attr-defined]

    async def test_execute_rotated(self) -> None:
        """Test execute with rotate instruction."""
        self.aio.rotate(45)
        editor = await self.aio.execute()
        self.assertIsInstance(editor, Editor)

    async def test_gather_returns_editors_in_order(self) -> None:
        """Test gather builds one Editor per source in input order."""

        def as_bytes(canvas: Canvas) -> BytesIO:
            buf = BytesIO()
            Editor(canvas).image.save(buf, format="PNG")
            buf.seek(0)
            return buf

        red = Canvas((10, 10), color="red")
        green = Canvas((20, 20), color="green")
        blue_bytes = as_bytes(Canvas((30, 30), color="blue"))

        editors = await AioEditor.gather([red, green, blue_bytes])

        self.assertEqual(len(editors), 3)
        for editor in editors:
            self.assertIsInstance(editor, Editor)
        # Order is preserved: sizes match the input sources.
        self.assertEqual(editors[0].image.size, (10, 10))
        self.assertEqual(editors[1].image.size, (20, 20))
        self.assertEqual(editors[2].image.size, (30, 30))

    async def test_gather_empty(self) -> None:
        """Test gather with no sources returns an empty list."""
        editors = await AioEditor.gather([])
        self.assertEqual(editors, [])

    async def test_gather_propagates_exceptions(self) -> None:
        """Test gather lets construction exceptions propagate."""
        with self.assertRaises((TypeError, ValueError, AttributeError, OSError)):
            await AioEditor.gather([object()])  # type: ignore[list-item]

    async def test_from_url(self) -> None:
        """Test from_url wraps the loaded image without real network."""
        loaded = Image.new("RGBA", (40, 40), "purple")

        async def fake_load(url: str) -> Image.Image:
            self.assertEqual(url, "http://example.com/avatar.png")
            return loaded

        import easy_pil.utils as utils_module

        prev = utils_module.load_image_async
        utils_module.load_image_async = fake_load  # type: ignore[assignment]
        try:
            aio = await AioEditor.from_url("http://example.com/avatar.png")
        finally:
            utils_module.load_image_async = prev  # type: ignore[assignment]

        self.assertIsInstance(aio, AioEditor)
        self.assertIs(aio.image, loaded)
        editor = await aio.execute()
        self.assertIsInstance(editor, Editor)


if __name__ == "__main__":
    unittest.main()
