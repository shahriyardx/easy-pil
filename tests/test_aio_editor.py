"""Tests for aio_editor."""

import unittest

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


if __name__ == "__main__":
    unittest.main()
