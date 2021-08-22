GET_INVERTER_REALTIME_DATA_SCOPE_DEVICE = {
    "timestamp": {"value": "2020-09-18T14:14:24-07:00"},
    "status": {"Code": 0, "Reason": "", "UserMessage": ""},
    "energy_day": {"value": 6000, "unit": "Wh"},
    "energy_total": {"value": 35611000, "unit": "Wh"},
    "energy_year": {"value": 3310000, "unit": "Wh"},
    "frequency_ac": {"value": 60, "unit": "Hz"},
    "current_ac": {"value": 7.31, "unit": "A"},
    "current_dc": {"value": 6.54, "unit": "A"},
    "power_ac": {"value": 1762, "unit": "W"},
    "voltage_ac": {"value": 241, "unit": "V"},
    "voltage_dc": {"value": 286, "unit": "V"},
    "status_code": {"value": 7},
    "error_code": {"value": 0},
    "led_state": {"value": 0},
    "led_color": {"value": 2},
}

GET_INVERTER_REALTIME_DATA_SYSTEM = {
    "timestamp": {"value": "2020-09-18T14:13:49-07:00"},
    "status": {"Code": 0, "Reason": "", "UserMessage": ""},
    "energy_day": {"value": 6000, "unit": "Wh"},
    "energy_total": {"value": 35611000, "unit": "Wh"},
    "energy_year": {"value": 3310000, "unit": "Wh"},
    "power_ac": {"value": 1764, "unit": "W"},
    "inverters": {
        "1": {
            "energy_day": {"value": 6000, "unit": "Wh"},
            "energy_total": {"value": 35611000, "unit": "Wh"},
            "energy_year": {"value": 3310000, "unit": "Wh"},
            "power_ac": {"value": 1764, "unit": "W"},
        }
    },
}
GET_LOGGER_INFO = {
    "timestamp": {"value": "2021-08-17T14:36:40+02:00"},
    "status": {"Code": 0, "Reason": "", "UserMessage": ""},
    "co2_factor": {"value": 0.5299999713897705, "unit": "kg/kWh"},
    "cash_factor": {"value": 0.07599999755620956, "unit": "EUR/kWh"},
    "hardware_version": {"value": "2.4E"},
    "software_version": {"value": "3.18.7-1"},
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
            "DT": 192,
            "PVPower": 5000,
            "UniqueID": "123456",
            "ErrorCode": 0,
            "StatusCode": 7,
            "CustomName": "",
        },
        {
            "device_id": "2",
            "DT": 192,
            "PVPower": 5000,
            "UniqueID": "234567",
            "ErrorCode": 0,
            "StatusCode": 7,
            "CustomName": "",
        },
    ]
}
