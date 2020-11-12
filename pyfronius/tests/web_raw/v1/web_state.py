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
            "power_ac": {"value": 0, "unit": "Wh"},
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
