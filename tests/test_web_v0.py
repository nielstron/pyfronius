#!/usr/bin/env python
# -*- coding: utf-8 -*-

# general requirements
import unittest

from tests.util import AsyncTestCaseSetup
from .test_structure.server_control import Server
from .test_structure.fronius_mock_server import FroniusRequestHandler, FroniusServer
from http.server import SimpleHTTPRequestHandler

# For the server in this case
import time

# For the tests
import aiohttp
import pyfronius
from tests.web_raw.v0.web_state import (
    GET_INVERTER_REALTIME_DATA_SCOPE_DEVICE,
    GET_INVERTER_REALTIME_DATA_SYSTEM,
    GET_LOGGER_INFO,
    GET_INVERTER_INFO,
)

ADDRESS = "localhost"


class NoFroniusWebTest(AsyncTestCaseSetup):
    server = None
    api_version = pyfronius.API_VERSION.V0
    server_control = None
    port = 0
    url = "http://localhost:80"
    session = None
    fronius = None

    async def test_no_server(self):
        # set up a fronius client and aiohttp session
        self.session = aiohttp.ClientSession()
        self.fronius = pyfronius.Fronius(self.session, self.url, self.api_version)
        try:
            await self.fronius.current_system_inverter_data()
            self.fail("No Exception for failed connection to fronius")
        except ConnectionError:
            await self.session.close()

    async def test_wrong_server(self):
        # This request handler ignores queries and should return the error page
        handler = SimpleHTTPRequestHandler

        max_retries = 10
        r = 0
        while not self.server:
            try:
                # Connect to any open port
                self.server = FroniusServer(
                    (ADDRESS, 0), handler, self.api_version.value
                )
            except OSError:
                if r < max_retries:
                    r += 1
                else:
                    raise
                time.sleep(1)

        self.server_control = Server(self.server)
        self.port = self.server_control.get_port()
        self.url = "http://{}:{}".format(ADDRESS, self.port)
        # Start test server before running any tests
        self.server_control.start_server()
        # set up a fronius client and aiohttp session
        self.session = aiohttp.ClientSession()
        self.fronius = pyfronius.Fronius(self.session, self.url, self.api_version)
        try:
            await self.fronius.current_system_inverter_data()
            self.fail("No Exception for wrong reply by host")
        except pyfronius.NotSupportedError:
            pass
        finally:
            await self.session.close()


class FroniusWebDetectVersionV0(AsyncTestCaseSetup):
    server = None
    api_version = pyfronius.API_VERSION.V0
    server_control = None
    port = 0
    url = "http://localhost:80"
    session = None
    fronius = None

    async def setUp(self):
        # Create an arbitrary subclass of TCP Server as the server to be
        # started
        # Here, it is an Simple HTTP file serving server
        handler = FroniusRequestHandler

        max_retries = 10
        r = 0
        while not self.server:
            try:
                # Connect to any open port
                self.server = FroniusServer(
                    (ADDRESS, 0), handler, self.api_version.value
                )
            except OSError:
                if r < max_retries:
                    r += 1
                else:
                    raise
                time.sleep(1)

        self.server_control = Server(self.server)
        self.port = self.server_control.get_port()
        self.url = "http://{}:{}".format(ADDRESS, self.port)
        # Start test server before running any tests
        self.server_control.start_server()
        # set up a fronius client and aiohttp session
        self.session = aiohttp.ClientSession()
        self.fronius = pyfronius.Fronius(self.session, self.url)  # auto api_version

    async def test_fronius_get_correct_api_version(self):
        # fetch any data to check if the correct api_version is retreived
        res = await self.fronius.current_inverter_data()
        self.assertEqual(res, GET_INVERTER_REALTIME_DATA_SCOPE_DEVICE)
        self.assertEqual(self.fronius.api_version, self.api_version)


class FroniusWebTestV0(AsyncTestCaseSetup):
    server = None
    api_version = pyfronius.API_VERSION.V0
    server_control = None
    port = 0
    url = "http://localhost:80"
    session = None
    fronius = None

    async def setUp(self):
        # Create an arbitrary subclass of TCP Server as the server to be
        # started
        # Here, it is an Simple HTTP file serving server
        handler = FroniusRequestHandler

        max_retries = 10
        r = 0
        while not self.server:
            try:
                # Connect to any open port
                self.server = FroniusServer(
                    (ADDRESS, 0), handler, self.api_version.value
                )
            except OSError:
                if r < max_retries:
                    r += 1
                else:
                    raise
                time.sleep(1)

        self.server_control = Server(self.server)
        self.port = self.server_control.get_port()
        self.url = "http://{}:{}".format(ADDRESS, self.port)
        # Start test server before running any tests
        self.server_control.start_server()
        # set up a fronius client and aiohttp session
        self.session = aiohttp.ClientSession()
        self.fronius = pyfronius.Fronius(self.session, self.url, self.api_version)

    async def test_fronius_get_inverter_realtime_data_device(self):
        res = await self.fronius.current_inverter_data()
        self.assertDictEqual(res, GET_INVERTER_REALTIME_DATA_SCOPE_DEVICE)

    async def test_fronius_get_inverter_realtime_data_system(self):
        res = await self.fronius.current_system_inverter_data()
        self.assertDictEqual(res, GET_INVERTER_REALTIME_DATA_SYSTEM)

    async def test_fronius_get_meter_realtime_data_system(self):
        with self.assertRaises(pyfronius.NotSupportedError):
            await self.fronius.current_system_meter_data()

    async def test_fronius_get_meter_realtime_data_device(self):
        with self.assertRaises(pyfronius.NotSupportedError):
            await self.fronius.current_meter_data()

    async def test_fronius_get_power_flow_realtime_data(self):
        with self.assertRaises(pyfronius.NotSupportedError):
            await self.fronius.current_power_flow()

    async def test_fronius_get_led_info_data(self):
        with self.assertRaises(pyfronius.NotSupportedError):
            await self.fronius.current_led_data()

    async def test_fronius_get_active_device_info(self):
        with self.assertRaises(pyfronius.NotSupportedError):
            await self.fronius.current_active_device_info()

    async def test_fronius_get_logger_info(self):
        res = await self.fronius.current_logger_info()
        self.assertDictEqual(res, GET_LOGGER_INFO)

    async def test_fronius_get_inverter_info(self):
        res = await self.fronius.inverter_info()
        self.assertDictEqual(res, GET_INVERTER_INFO)

    async def test_fronius_get_no_data(self):
        # Storage data for device 0 is not provided ATM
        # TODO someone add some storage data for a device 1?
        with self.assertRaises(pyfronius.NotSupportedError):
            await self.fronius.current_storage_data()

    async def tearDown(self):
        await self.session.close()
        self.server_control.stop_server()
        pass


if __name__ == "__main__":
    unittest.main()
