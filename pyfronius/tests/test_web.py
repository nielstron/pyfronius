#!/usr/bin/env python
# -*- coding: utf-8 -*-

# general requirements
import unittest
from .test_structure.server_control import Server
from .test_structure.fronius_mock_server import FroniusRequestHandler, FroniusServer
from http.server import SimpleHTTPRequestHandler

# For the server in this case
import time

# For the tests
import aiohttp
import asyncio
import pyfronius
from .web_raw.web_state import (
    GET_METER_REALTIME_DATA_SCOPE_DEVICE, GET_METER_REALTIME_DATA_SYSTEM,
    GET_POWER_FLOW_REALTIME_DATA, GET_INVERTER_REALTIME_DATA_SCOPE_DEVICE,
    GET_INVERTER_REALTIME_DATA_SYSTEM, GET_STORAGE_REALTIME_DATA_SCOPE_DEVICE,
    GET_LOGGER_LED_INFO_STATE)

ADDRESS = 'localhost'


class NoFroniusWebTest(unittest.TestCase):

    server = None
    server_control = None
    port = 0
    url = 'http://localhost:80'
    session = None
    fronius = None

    def test_no_server(self):
        # set up a fronius client and aiohttp session
        self.session = aiohttp.ClientSession()
        self.fronius = pyfronius.Fronius(self.session, self.url)
        try:
            res = asyncio.get_event_loop().run_until_complete(
                self.fronius.current_system_meter_data())
            self.fail("No Exception for failed connection to fronius")
        except ConnectionError:
            asyncio.get_event_loop().run_until_complete(self.session.close())

    def test_wrong_server(self):
        # This request handler ignores queries and should return the error page
        handler = SimpleHTTPRequestHandler

        max_retries = 10
        r = 0
        while not self.server:
            try:
                # Connect to any open port
                self.server = FroniusServer((ADDRESS, 0), handler)
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
        self.fronius = pyfronius.Fronius(self.session, self.url)
        try:
            res = asyncio.get_event_loop().run_until_complete(
                self.fronius.current_system_meter_data())
            self.fail("No Exception for wrong reply by host")
        except ValueError:
            asyncio.get_event_loop().run_until_complete(self.session.close())


class FroniusWebTest(unittest.TestCase):

    server = None
    server_control = None
    port = 0
    url = 'http://localhost:80'
    session = None
    fronius = None

    def setUp(self):
        # Create an arbitrary subclass of TCP Server as the server to be started
        # Here, it is an Simple HTTP file serving server
        handler = FroniusRequestHandler

        max_retries = 10
        r = 0
        while not self.server:
            try:
                # Connect to any open port
                self.server = FroniusServer((ADDRESS, 0), handler)
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
        self.fronius = pyfronius.Fronius(self.session, self.url)

    def test_fronius_get_meter_realtime_data_system(self):
        res = asyncio.get_event_loop().run_until_complete(
            self.fronius.current_system_meter_data())
        self.assertEqual(res, GET_METER_REALTIME_DATA_SYSTEM)

    def test_fronius_get_meter_realtime_data_device(self):
        res = asyncio.get_event_loop().run_until_complete(
            self.fronius.current_meter_data())
        print(res)
        self.assertEqual(res, GET_METER_REALTIME_DATA_SCOPE_DEVICE)

    def test_fronius_get_power_flow_realtime_data(self):
        res = asyncio.get_event_loop().run_until_complete(
            self.fronius.current_power_flow())
        self.assertEqual(res, GET_POWER_FLOW_REALTIME_DATA)

    def test_fronius_get_inverter_realtime_data_device(self):
        res = asyncio.get_event_loop().run_until_complete(
            self.fronius.current_inverter_data())
        self.assertEqual(res, GET_INVERTER_REALTIME_DATA_SCOPE_DEVICE)

    def test_fronius_get_inverter_realtime_data_system(self):
        res = asyncio.get_event_loop().run_until_complete(
            self.fronius.current_system_inverter_data())
        self.assertEqual(res, GET_INVERTER_REALTIME_DATA_SYSTEM)

    def test_fronius_get_led_info_data(self):
        res = asyncio.get_event_loop().run_until_complete(
            self.fronius.current_led_data())
        print(res)
        self.assertEqual(res, GET_LOGGER_LED_INFO_STATE)

    def test_fronius_get_no_data(self):
        # Storage data for device 0 is not provided ATM
        # TODO someone add some storage data for a device 1?
        res = asyncio.get_event_loop().run_until_complete(
            self.fronius.current_storage_data())
        self.assertIn('timestamp', res)
        self.assertIn('status', res)
        # Mainly asserts that no error is thrown by illegal access!

    def test_fronius_fetch(self):
        res = asyncio.get_event_loop().run_until_complete(self.fronius.fetch())
        self.assertEqual(res, [
            GET_POWER_FLOW_REALTIME_DATA, GET_METER_REALTIME_DATA_SYSTEM,
            GET_INVERTER_REALTIME_DATA_SYSTEM,
            GET_METER_REALTIME_DATA_SCOPE_DEVICE,
            GET_STORAGE_REALTIME_DATA_SCOPE_DEVICE,
            GET_INVERTER_REALTIME_DATA_SCOPE_DEVICE
        ])

    def tearDown(self):
        asyncio.get_event_loop().run_until_complete(self.session.close())
        self.server_control.stop_server()
        pass


if __name__ == "__main__":
    unittest.main()
