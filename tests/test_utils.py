"""Tests for utils."""

import unittest

import aiohttp
from PIL import Image

from easy_pil import AioEditor, Canvas, Editor, load_image, load_image_async
from easy_pil.utils import run_in_executor

_TEST_URL = "http://httpbin.org/image/png"


class TestUtils(unittest.IsolatedAsyncioTestCase):
    """Tests for utility functions."""

    def test_load_image(self) -> None:
        """Test loading an image from a URL."""
        try:
            img = load_image(_TEST_URL)
        except OSError:
            self.skipTest("network unavailable")
        assert isinstance(img, Image.Image)

    async def test_load_image_async(self) -> None:
        """Test loading an image asynchronously."""
        try:
            img = await load_image_async(_TEST_URL)
        except OSError:
            self.skipTest("network unavailable")
        assert isinstance(img, Image.Image)

    async def test_cache(self) -> None:
        """Test caching of loaded images."""
        try:
            img1 = await load_image_async(_TEST_URL)
            img2 = await load_image_async(_TEST_URL)
        except OSError:
            self.skipTest("network unavailable")

        assert isinstance(img1, Image.Image)
        assert isinstance(img2, Image.Image)

        img3 = load_image(_TEST_URL)
        img4 = load_image(_TEST_URL)

        assert isinstance(img3, Image.Image)
        assert isinstance(img4, Image.Image)

    async def test_aio_editor(self) -> None:
        """Test AioEditor execution."""
        canvas = Canvas((100, 100), color="black")
        aio = AioEditor(canvas)
        editor = await aio.execute()

        assert isinstance(editor, Editor)

    async def test_load_image_async_no_session(self) -> None:
        """Test load_image_async without existing session."""
        try:
            img = await load_image_async(_TEST_URL)
        except OSError:
            self.skipTest("network unavailable")
        assert isinstance(img, Image.Image)

    async def test_load_image_async_with_session(self) -> None:
        """Test load_image_async with aiohttp session."""
        try:
            async with aiohttp.ClientSession() as session:
                img = await load_image_async(_TEST_URL, session=session)
        except OSError:
            self.skipTest("network unavailable")
        assert isinstance(img, Image.Image)

    async def test_run_in_executor(self) -> None:
        """Test run_in_executor utility."""
        result = await run_in_executor(Image.new, mode="RGBA", size=(10, 10))
        self.assertIsInstance(result, Image.Image)


if __name__ == "__main__":
    unittest.main()
