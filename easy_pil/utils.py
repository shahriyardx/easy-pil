"""Utility functions for loading and processing images."""

import asyncio
import functools
from collections.abc import Callable
from io import BytesIO
from typing import Any

import aiohttp
import requests
from PIL import Image
from PIL.GifImagePlugin import GifImageFile


async def run_in_executor(func: Callable[..., Any], **kwargs: Any) -> Any:
    """Run function in executor."""
    func = functools.partial(func, **kwargs)
    return await asyncio.get_running_loop().run_in_executor(None, func)


def load_image(
    link: str,
    *,
    raw: bool = False,
) -> Image.Image | GifImageFile:
    """
    Load image from link.

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
    resp = requests.get(link, timeout=30)
    resp.raise_for_status()
    _bytes = BytesIO(resp.content)
    image = Image.open(_bytes)
    if not raw:
        image = image.convert("RGBA")

    return image


async def load_image_async(
    link: str,
    session: aiohttp.ClientSession | None = None,
    *,
    raw: bool = False,
) -> Image.Image | GifImageFile:
    """
    Load image from link (async).

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
    timeout = aiohttp.ClientTimeout(total=30)
    if isinstance(session, aiohttp.ClientSession):
        async with session.get(link, timeout=timeout) as response:
            response.raise_for_status()
            _bytes = BytesIO(await response.read())
    else:
        async with (
            aiohttp.ClientSession() as new_session,
            new_session.get(link, timeout=timeout) as response,
        ):
            response.raise_for_status()
            _bytes = BytesIO(await response.read())

    image = Image.open(_bytes)
    if not raw:
        image = image.convert("RGBA")

    return image
