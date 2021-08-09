import functools
import asyncio


async def run_in_executor(func, **kwargs):
    func = functools.partial(func, **kwargs)
    data = await asyncio.get_event_loop().run_in_executor(None, func)
    return data
