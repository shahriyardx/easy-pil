import asyncio
import functools
from functools import lru_cache
from io import BytesIO
from typing import Union, Optional

import aiohttp
import requests
from aiocache import cached
from PIL import Image
from PIL.GifImagePlugin import GifImageFile


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


@lru_cache(maxsize=32)
def load_image(
    link: str, raw: bool = False
) -> Union[Image.Image, GifImageFile]:
    """Load image from link

    Parameters
    ----------
    link : str
        Image link
    raw: bool
        if you want the raw image without any conversion

    Returns
    -------
    PIL.Image.Image
        Image from the provided link (if any)
    """
    _bytes = BytesIO(requests.get(link).content)
    image = Image.open(_bytes)
    if not raw:
        image = image.convert("RGBA")

    return image


@cached(ttl=60 * 60 * 24)
async def load_image_async(
    link: str, session: Optional[aiohttp.ClientSession] = None, raw: bool = False
) -> Union[Image.Image, GifImageFile]:
    """Load image from link (async)

    Parameters
    ----------
    link : str
        Image from the provided link (if any)
    session: aiohttp.ClientSession
        clientSession for making requests, defaults to None
    raw: bool
        if you want the raw image without any conversion

    Returns
    -------
    PIL.Image.Image
        Image link
    """
    if isinstance(session, aiohttp.ClientSession):
        async with session.get(link) as response:  # type: ignore
            data = await response.read()
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                data = await response.read()

    _bytes = BytesIO(data)
    image = Image.open(_bytes)
    if not raw:
        image = image.convert("RGBA")

    return image
