#!/usr/bin/env python
# -*- coding: utf-8 -*-

# general requirements
import unittest

# for the tests
from .web_raw.v1 import web_state
from pyfronius import Fronius


class FroniusHelperTest(unittest.TestCase):
    def test_error_code(self):
        res = web_state.GET_INVERTER_REALTIME_DATA_SCOPE_DEVICE
        self.assertEqual(Fronius.error_code(res), 0)
        res = web_state.GET_STORAGE_REALTIME_DATA_SCOPE_DEVICE
        self.assertEqual(Fronius.error_code(res), 255)

    def test_error_reason(self):
        res = web_state.GET_INVERTER_REALTIME_DATA_SCOPE_DEVICE
        self.assertEqual(Fronius.error_reason(res), "")
        res = web_state.GET_STORAGE_REALTIME_DATA_SCOPE_DEVICE
        self.assertEqual(Fronius.error_reason(res), "Storages are not supported")
