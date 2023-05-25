import unittest

from PIL import Image

from easy_pil import AioEditor, Canvas, Editor, load_image, load_image_async


class TestUtils(unittest.IsolatedAsyncioTestCase):
    url: str = (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/"
        "f/f9/Flag_of_Bangladesh.svg/800px-Flag_of_Bangladesh.svg.png"
    )

    def test_load_image(self):
        img = load_image(self.url)
        self.assertIsInstance(img, Image.Image)

    async def test_load_image_async(self):
        img = await load_image_async(self.url)
        self.assertIsInstance(img, Image.Image)

    async def test_cache(self):
        img1 = await load_image_async(self.url)
        img2 = await load_image_async(self.url)

        self.assertIsInstance(img1, Image.Image)
        self.assertIsInstance(img2, Image.Image)

        img3 = load_image(self.url)
        img4 = load_image(self.url)

        self.assertIsInstance(img3, Image.Image)
        self.assertIsInstance(img4, Image.Image)

    async def test_aio_editor(self):
        canvas = Canvas((100, 100), color="black")
        aio = AioEditor(canvas)
        editor = await aio.execute()

        self.assertIsInstance(editor, Editor)


if __name__ == "__main__":
    unittest.main()
