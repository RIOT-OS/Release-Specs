"""
Helpers for asyncio
"""

import asyncio


def wait_for_futures(futures):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*futures))


def timeout_futures(futures, timeout):
    gather = None

    async def wait_for_timeout():
        await asyncio.sleep(timeout)
        if gather:
            return gather.cancel()
        return False

    gather = asyncio.gather(wait_for_timeout(), *futures)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(gather)
    except asyncio.CancelledError:
        pass
