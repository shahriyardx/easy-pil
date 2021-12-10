import asyncio
import functools
from io import BytesIO

import aiohttp
import requests
from PIL import Image


async def run_in_executor(func, **kwargs):
    """Run function is executor

    :param func: Function to run
    :type func: func
    :return: Any
    :rtype: Any
    """
    func = functools.partial(func, **kwargs)
    data = await asyncio.get_event_loop().run_in_executor(None, func)
    return data


def load_image(link: str):
    """Load image from link

    :param link: Image link
    :type link: str
    :return: Image from link
    :rtype: Image.Image
    """
    _bytes = BytesIO(requests.get(link).content)
    image = Image.open(_bytes).convert("RGBA")

    return image


async def load_image_async(link: str):
    """Load image from link (async)

    :param link: Image link
    :type link: str
    :return: Image from link
    :rtype: Image.Image
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as response:
            data = await response.read()

    _bytes = BytesIO(data)
    image = Image.open(_bytes).convert("RGBA")
    return image
