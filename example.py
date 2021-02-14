#!/usr/bin/env python
"""Basic usage example and testing of pyfronius."""
import asyncio
import logging
import sys
import aiohttp

import pyfronius


async def main(loop, host):
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(loop=loop, timeout=timeout) as session:
        fronius = pyfronius.Fronius(session, host)

        res = await fronius.fetch(loop=loop)
        for r in res:
            print(r)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop, sys.argv[1]))
