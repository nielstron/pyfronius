#!/usr/bin/env python
"""Basic usage example and testing of pyfronius."""
import asyncio
import logging
import sys

import aiohttp

import pyfronius
from pyfronius import _LOGGER


@asyncio.coroutine
def main(loop, host):
    session = aiohttp.ClientSession(loop=loop)
    fronius = pyfronius.Fronius(session, host)

    while loop.jk_run:
        res = yield from fronius.current_power_flow()
        _LOGGER.debug(res)
        res = yield from fronius.current_system_meter_data()
        _LOGGER.debug(res)
        res = yield from fronius.current_meter_data()
        _LOGGER.debug(res)
        res = yield from fronius.current_storage_data()
        _LOGGER.debug(res)
        res = yield from fronius.current_inverter_data()
        _LOGGER.debug(res)
        res = yield from fronius.current_system_inverter_data()
        _LOGGER.debug(res)
        yield from asyncio.sleep(5)

    yield from session.close()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    try:
        setattr(loop, "jk_run", True)
        loop.run_until_complete(main(loop, "172.31.106.11"))
    except KeyboardInterrupt:
        setattr(loop, "jk_run", False)
        loop.run_forever()
