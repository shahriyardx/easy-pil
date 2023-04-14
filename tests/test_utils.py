import unittest

from PIL import Image

from easy_pil import load_image, load_image_async


class TestUtils(unittest.IsolatedAsyncioTestCase):
    def test_load_image(self):
        img = load_image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Flag_of_Bangladesh.svg/800px-Flag_of_Bangladesh.svg.png"
        )

        self.assertIsInstance(img, Image.Image)

    async def test_load_image_async(self):
        img = await load_image_async(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Flag_of_Bangladesh.svg/800px-Flag_of_Bangladesh.svg.png"
        )

        self.assertIsInstance(img, Image.Image)


if __name__ == "__main__":
    unittest.main()
