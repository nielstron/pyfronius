#!/usr/bin/env python
"""Basic usage example and testing of pyfronius."""
import asyncio
import logging
import sys

import aiohttp

import pyfronius


async def main(loop, host):
    async with aiohttp.ClientSession(loop=loop) as session:
        fronius = pyfronius.Fronius(session, host)

        res = await fronius.current_power_flow()
        print(res)
        res = await fronius.current_system_meter_data()
        print(res)
        res = await fronius.current_meter_data()
        print(res)
        res = await fronius.current_storage_data()
        print(res)
        res = await fronius.current_inverter_data()
        print(res)
        res = await fronius.current_system_inverter_data()
        print(res)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop, "http://172.31.106.11"))
