GET_POWER_FLOW_REALTIME_DATA = {
    "timestamp": {"value": "2019-01-10T23:33:12+01:00"},
    "status": {"Code": 0, "Reason": "", "UserMessage": ""},
    "energy_day": {"value": 0, "unit": "Wh"},
    "energy_total": {"value": 26213502, "unit": "Wh"},
    "energy_year": {"value": 12400.100586, "unit": "Wh"},
    "meter_location": {"value": "load"},
    "meter_mode": {"value": "vague-meter"},
    "power_battery": {"value": None, "unit": "W"},
    "power_grid": {"value": 367.722145, "unit": "W"},
    "power_load": {"value": -367.722145, "unit": "W"},
    "power_photovoltaics": {"value": None, "unit": "W"},
}

GET_METER_REALTIME_DATA_SYSTEM = {
    "timestamp": {"value": "2019-01-10T23:33:13+01:00"},
    "status": {"Code": 0, "Reason": "", "UserMessage": ""},
    "meters": {
        "0": {
            "power_real": {"value": -367.722145, "unit": "W"},
            "meter_location": {"value": 1},
            "enable": {"value": 1},
            "visible": {"value": 1},
            "manufacturer": {"value": "Fronius"},
            "model": {"value": ""},
            "serial": {"value": ""},
        }
    },
}

GET_METER_REALTIME_DATA_SCOPE_DEVICE = {
    "timestamp": {"value": "2019-01-10T23:33:14+01:00"},
    "status": {"Code": 0, "Reason": "", "UserMessage": ""},
    "power_real": {"value": -367.722145, "unit": "W"},
    "meter_location": {"value": 1},
    "enable": {"value": 1},
    "visible": {"value": 1},
    "manufacturer": {"value": "Fronius"},
    "model": {"value": ""},
    "serial": {"value": ""},
}

GET_INVERTER_REALTIME_DATA_SCOPE_DEVICE = {
    "timestamp": {"value": "2019-01-10T23:33:15+01:00"},
    "status": {"Code": 0, "Reason": "", "UserMessage": ""},
    "energy_day": {"value": 0, "unit": "Wh"},
    "energy_total": {"value": 26213502, "unit": "Wh"},
    "energy_year": {"value": 12400.1, "unit": "Wh"},
    "status_code": {"value": 3},
    "error_code": {"value": 523},
    "led_state": {"value": 0},
    "led_color": {"value": 1},
}

GET_STORAGE_REALTIME_DATA_SCOPE_DEVICE = {
    "timestamp": {"value": "2019-01-10T23:33:14+01:00"},
    "status": {"Code": 255, "Reason": "Storages are not supported", "UserMessage": ""},
}

GET_INVERTER_REALTIME_DATA_SYSTEM = {
    "timestamp": {"value": "2019-01-10T23:33:16+01:00"},
    "status": {"Code": 0, "Reason": "", "UserMessage": ""},
    "energy_day": {"value": 0, "unit": "Wh"},
    "energy_total": {"value": 26213502, "unit": "Wh"},
    "energy_year": {"value": 12400, "unit": "Wh"},
    "power_ac": {"value": 0, "unit": "W"},
    "inverters": {
        "1": {
            "energy_day": {"value": 0, "unit": "Wh"},
            "energy_total": {"value": 26213502, "unit": "Wh"},
            "energy_year": {"value": 12400, "unit": "Wh"},
            "power_ac": {"value": 0, "unit": "W"},
        }
    },
}

GET_LOGGER_LED_INFO_STATE = {
    "timestamp": {"value": "2019-06-23T23:50:16+02:00"},
    "status": {"Code": 0, "Reason": "", "UserMessage": ""},
    "power_led": {"color": "green", "state": "on"},
    "solar_net_led": {"color": "green", "state": "on"},
    "solar_web_led": {"color": "none", "state": "off"},
    "wlan_led": {"color": "green", "state": "on"},
}

GET_ACTIVE_DEVICE_INFO = {
    "timestamp": {"value": "2021-08-17T14:12:17+02:00"},
    "status": {"Code": 0, "Reason": "", "UserMessage": ""},
    "inverters": [{"device_id": "1", "device_type": 122, "serial_number": "30412345"}],
    "meters": [{"device_id": "0", "serial_number": "18412345"}],
    "ohmpilots": [],
    "sensor_cards": [],
    "storages": [],
    "string_controls": [],
}

GET_LOGGER_INFO = {
    "timestamp": {"value": "2021-08-17T14:36:40+02:00"},
    "status": {"Code": 0, "Reason": "", "UserMessage": ""},
    "co2_factor": {"value": 0.5299999713897705, "unit": "kg/kWh"},
    "cash_factor": {"value": 0.07599999755620956, "unit": "EUR/kWh"},
    "delivery_factor": {"value": 0.15000000596046448, "unit": "EUR/kWh"},
    "hardware_version": {"value": "2.4E"},
    "software_version": {"value": "3.18.7-1"},
    "hardware_platform": {"value": "wilma"},
    "product_type": {"value": "fronius-datamanager-card"},
    "time_zone_location": {"value": "Vienna"},
    "time_zone": {"value": "CEST"},
    "utc_offset": {"value": 7200},
    "unique_identifier": {"value": "240.123456"},
}

GET_INVERTER_INFO = {

    "timestamp": {"value": "2019-06-12T15:31:02+02:00"},
    "status": {"Code": 0, "Reason": "", "UserMessage": ""},
    "inverters": [
        {
            "device_id": "1",
            "custom_name": "Primo 8.2-1 (",
            "device_type": 102,
            "error_code": 0,
            "pv_power": {
                "value": 500,
                "unit": "W",
                },
            "show": 1,
            "status_code": 7,
            "unique_id": "38183",
        },
        {
            "device_id": "2",
            "custom_name": "Primo 5.0-1 20",
            "device_type": 86,
            "error_code": 0,
            "pv_power": {
                "value": 500,
                "unit": "W",
                },
            "show": 1,
            "status_code": 7,
            "unique_id": "16777215",
        },
        {
            "device_id": "3",
            "custom_name": "Galvo 3.1-1 20",
            "device_type": 106,
            "error_code": 0,
            "pv_power": {
                "value": 500,
                "unit": "W",
                },
            "show": 1,
            "status_code": 7,
            "unique_id": "7262",
        },
        {
            "device_id": "55",
            "custom_name": "Galvo 3.0-1 (5",
            "device_type": 224,
            "error_code": 0,
            "pv_power": {
                "value": 500,
                "unit": "W",
                },
            "show": 1,
            "status_code": 7,
            "unique_id": "100372",
        },
        {
            "device_id": "240",
            "custom_name" : "tr-3pn-01",
            "device_type": 1,
            "error_code": None,
            "pv_power" : {
                "value": 0,
                "unit": "W",
                },
            "show" : 1,
            "status_code" : "Running",
            "unique_id" : "29301000987160033"
        },
    ]
}
