"""
Helpers for asyncio
"""

import asyncio


def wait_for_futures(futures):
    async def gather_futures(futures):
        await asyncio.gather(*futures)

    asyncio.run(gather_futures(futures))


def timeout_futures(futures, timeout):
    async def wait_for_timeout(futures, timeout):
        try:
            await asyncio.wait_for(asyncio.gather(*futures), timeout=timeout)
        except TimeoutError:
            pass

    asyncio.run(wait_for_timeout(futures, timeout))
