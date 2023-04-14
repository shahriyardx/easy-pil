import asyncio
import functools
from io import BytesIO

import aiohttp
import requests
from memoization import cached
from PIL import Image


async def run_in_executor(func, **kwargs):
    """Run function in executor

    Parameters
    ----------
    func : func
        Function to run
    """
    func = functools.partial(func, **kwargs)
    data = await asyncio.get_event_loop().run_in_executor(None, func)
    return data


@cached(max_size=50)
def load_image(link: str) -> Image.Image:
    """Load image from link

    Parameters
    ----------
    link : str
        Image link

    Returns
    -------
    PIL.Image.Image
        Image from the provided link (if any)
    """
    _bytes = BytesIO(requests.get(link).content)
    image = Image.open(_bytes).convert("RGBA")

    return image


@cached(max_size=50)
async def load_image_async(link: str) -> Image.Image:
    """Load image from link (async)

    Parameters
    ----------
    link : str
        Image from the provided link (if any)

    Returns
    -------
    PIL.Image.Image
        Image link
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as response:
            data = await response.read()

    _bytes = BytesIO(data)
    image = Image.open(_bytes).convert("RGBA")
    return image
