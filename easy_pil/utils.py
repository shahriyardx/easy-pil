import asyncio
import functools
from io import BytesIO

import aiohttp
import requests
from PIL import Image


async def run_in_executor(func, **kwargs):
    """Run a function in a thread pool executor.
    
    Args:
        func: The function to run.
        **kwargs: The arguments to pass to the function.
    
    Returns:
        The result of the function.
    """
    func = functools.partial(func, **kwargs)
    data = await asyncio.get_event_loop().run_in_executor(None, func)
    return data


def load_image(link: str):
    """Load image from a link.
    
    Args:
        link: The link to the image.

    Returns:
        Image.Image: The image.
    """
    _bytes = BytesIO(requests.get(link).content)
    image = Image.open(_bytes).convert("RGBA")

    return image


async def load_image_async(link: str):
    """Load image from a link. (async)
    
    Args:
        link: The link to the image.

    Returns:
        Image.Image: The image.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as response:
            data = await response.read()

    _bytes = BytesIO(data)
    image = Image.open(_bytes).convert("RGBA")
    return image
