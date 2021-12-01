"""
Created on 27.09.2017

@author: Niels
@author: Gerrit Beine
"""

import asyncio
import enum
from html import unescape
import json
import logging
from typing import Any, Dict

import aiohttp

from .const import INVERTER_DEVICE_TYPE, OHMPILOT_STATE_CODES

_LOGGER = logging.getLogger(__name__)
DEGREE_CELSIUS = "°C"
WATT = "W"
WATT_HOUR = "Wh"
AMPERE = "A"
VOLT = "V"
PERCENT = "%"
HERTZ = "Hz"
VOLTAMPEREREACTIVE = "VAr"
VOLTAMPEREREACTIVE_HOUR = "VArh"
VOLTAMPERE = "VA"
PER_KILOWATTHOUR = "{}/kWh"


class API_VERSION(enum.Enum):
    value: int

    AUTO = -1
    V0 = 0
    V1 = 1


API_BASEPATHS = {
    API_VERSION.V0: "/solar_api/",
    API_VERSION.V1: "/solar_api/v1/",
}

URL_API_VERSION = "solar_api/GetAPIVersion.cgi"
URL_POWER_FLOW = {API_VERSION.V1: "GetPowerFlowRealtimeData.fcgi"}
URL_SYSTEM_METER = {API_VERSION.V1: "GetMeterRealtimeData.cgi?Scope=System"}
URL_SYSTEM_INVERTER = {
    API_VERSION.V0: "GetInverterRealtimeData.cgi?Scope=System",
    API_VERSION.V1: "GetInverterRealtimeData.cgi?Scope=System",
}
URL_SYSTEM_LED = {API_VERSION.V1: "GetLoggerLEDInfo.cgi"}
URL_SYSTEM_OHMPILOT = {API_VERSION.V1: "GetOhmPilotRealtimeData.cgi?Scope=System"}
URL_SYSTEM_STORAGE = {
    API_VERSION.V1: "GetStorageRealtimeData.cgi?Scope=System"
}
URL_DEVICE_METER = {API_VERSION.V1: "GetMeterRealtimeData.cgi?Scope=Device&DeviceId={}"}
URL_DEVICE_STORAGE = {
    API_VERSION.V1: "GetStorageRealtimeData.cgi?Scope=Device&DeviceId={}"
}
URL_DEVICE_INVERTER_CUMULATIVE = {
    API_VERSION.V0: (
        "GetInverterRealtimeData.cgi?Scope=Device&"
        "DeviceIndex={}&"
        "DataCollection=CumulationInverterData"
    ),
    API_VERSION.V1: (
        "GetInverterRealtimeData.cgi?Scope=Device&"
        "DeviceId={}&"
        "DataCollection=CumulationInverterData"
    ),
}
URL_DEVICE_INVERTER_COMMON = {
    API_VERSION.V0: (
        "GetInverterRealtimeData.cgi?Scope=Device&"
        "DeviceIndex={}&"
        "DataCollection=CommonInverterData"
    ),
    API_VERSION.V1: (
        "GetInverterRealtimeData.cgi?Scope=Device&"
        "DeviceId={}&"
        "DataCollection=CommonInverterData"
    ),
}
URL_ACTIVE_DEVICE_INFO_SYSTEM = {
    API_VERSION.V1: "GetActiveDeviceInfo.cgi?DeviceClass=System"
}
URL_INVERTER_INFO = {
    API_VERSION.V0: "GetInverterInfo.cgi",
    API_VERSION.V1: "GetInverterInfo.cgi",
}
URL_LOGGER_INFO = {
    API_VERSION.V0: "GetLoggerInfo.cgi",
    API_VERSION.V1: "GetLoggerInfo.cgi",
}

HEADER_STATUS_CODES = {
    0: "OKAY",
    1: "NotImplemented",
    2: "Uninitialized",
    3: "Initialized",
    4: "Running",
    5: "Timeout",
    6: "Argument Error",
    7: "LNRequestError",
    8: "LNRequestTimeout",
    9: "LNParseError",
    10: "ConfigIOError",
    11: "NotSupported",
    12: "DeviceNotAvailable",
    255: "UnknownError",
}


class FroniusError(Exception):
    """
    A superclass that covers all errors occuring during the
    connection to a Fronius device
    """


class NotSupportedError(ValueError, FroniusError):
    """
    An error to be raised if a specific feature
    is not supported by the specified device
    """


class ConnectionError(ConnectionError, FroniusError):
    """
    An error to be raised if the connection to the fronius device failed
    """


class InvalidAnswerError(ValueError, FroniusError):
    """
    An error to be raised if the host Fronius device could not answer a request
    """


class BadStatusError(FroniusError):
    """A bad status code was returned."""
    def __init__(
            self,
            endpoint: str,
            code: int,
            reason: str = None,
            response: Dict[str, Any] = {},
            ) -> None:
        """Instantiate exception."""
        self.response = response
        message = (
            f"BadStatusError at {endpoint}. "
            f"Code: {code} - {HEADER_STATUS_CODES.get(code, 'unknown status code')}. "
            f"Reason: {reason or 'unknown'}."
        )
        super().__init__(message)


class Fronius:
    """
    Interface to communicate with the Fronius Symo over http / JSON
    Timeouts are to be set in the given AIO session
    Attributes:
        session     The AIO session
        url         The url for reaching of the Fronius device
                    (i.e. http://192.168.0.10:80)
        api_version  Version of Fronius API to use
    """

    def __init__(
        self, session: aiohttp.ClientSession, url: str, api_version=API_VERSION.AUTO
    ):
        """
        Constructor
        """
        self._aio_session = session
        while url[-1] == "/":
            url = url[:-1]
        self.url = url
        # prepend http:// if missing, by fronius API this is the only supported protocol
        if not self.url.startswith("http"):
            self.url = "http://{}".format(self.url)
        self.api_version = api_version
        self.base_url = API_BASEPATHS.get(api_version)

    async def _fetch_json(self, url):
        """
        Fetch json value from fixed url
        """
        try:
            async with self._aio_session.get(url) as res:
                result = await res.json(content_type=None)
        except asyncio.TimeoutError:
            raise ConnectionError(
                "Connection to Fronius device timed out at {}.".format(url)
            )
        except aiohttp.ClientError:
            raise ConnectionError(
                "Connection to Fronius device failed at {}.".format(url)
            )
        except (aiohttp.ContentTypeError, json.decoder.JSONDecodeError):
            raise InvalidAnswerError(
                "Host returned a non-JSON reply at {}.".format(url)
            )
        return result

    async def fetch_api_version(self):
        """
        Fetches the highest supported API version of the initiated fronius device
        :return:
        """
        try:
            res = await self._fetch_json("{}/{}".format(self.url, URL_API_VERSION))
            api_version, base_url = API_VERSION(res["APIVersion"]), res["BaseURL"]
        except InvalidAnswerError:
            # Host returns 404 response if API version is 0
            api_version, base_url = API_VERSION.V0, API_BASEPATHS[API_VERSION.V0]

        return api_version, base_url

    async def _fetch_solar_api(self, spec, spec_name, *spec_formattings):
        """
        Fetch page of solar_api
        """
        # either unknown api version given or automatic
        if self.base_url is None:
            prev_api_version = self.api_version
            self.api_version, self.base_url = await self.fetch_api_version()
            if prev_api_version == API_VERSION.AUTO:
                _LOGGER.debug(
                    """using highest supported API version {}""".format(
                        self.api_version
                    )
                )
            if (
                prev_api_version != self.api_version
                and prev_api_version != API_VERSION.AUTO
            ):
                _LOGGER.warning(
                    (
                        """Unknown API version {} is not supported by host {},"""
                        """using highest supported API version {} instead"""
                    ).format(prev_api_version, self.url, self.api_version)
                )
        spec_url = spec.get(self.api_version)
        if spec_url is None:
            raise NotSupportedError(
                "API version {} does not support request of {} data".format(
                    self.api_version, spec_name
                )
            )
        if spec_formattings:
            spec_url = spec_url.format(*spec_formattings)

        _LOGGER.debug("Get {} data for {}".format(spec_name, spec_url))
        res = await self._fetch_json("{}{}{}".format(self.url, self.base_url, spec_url))
        return res

    async def fetch(
        self,
        active_device_info=True,
        inverter_info=True,
        logger_info=True,
        power_flow=True,
        system_meter=True,
        system_inverter=True,
        system_ohmpilot=True,
        system_storage=True,
        device_meter=frozenset(["0"]),
        # storage is not necessarily supported by every fronius device
        device_storage=frozenset(["0"]),
        device_inverter=frozenset(["1"]),
        loop=None,
    ):
        requests = []
        if active_device_info:
            requests.append(self.current_active_device_info())
        if inverter_info:
            requests.append(self.inverter_info())
        if logger_info:
            requests.append(self.current_logger_info())
        if power_flow:
            requests.append(self.current_power_flow())
        if system_meter:
            requests.append(self.current_system_meter_data())
        if system_inverter:
            requests.append(self.current_system_inverter_data())
        if system_ohmpilot:
            requests.append(self.current_system_ohmpilot_data())
        if system_storage:
            requests.append(self.current_system_storage_data())
        for i in device_meter:
            requests.append(self.current_meter_data(i))
        for i in device_storage:
            requests.append(self.current_storage_data(i))
        for i in device_inverter:
            requests.append(self.current_inverter_data(i))

        res = await asyncio.gather(*requests, loop=loop, return_exceptions=True)
        responses = []
        for result in res:
            if isinstance(result, FroniusError):
                _LOGGER.warning(result)
                if isinstance(result, BadStatusError):
                    responses.append(result.response)
                continue
            responses.append(result)
        return responses

    @staticmethod
    def _status_data(res):

        sensor = {}

        sensor["timestamp"] = {"value": res["Head"]["Timestamp"]}
        sensor["status"] = res["Head"]["Status"]

        return sensor

    @staticmethod
    def error_code(sensor_data):
        """
        Extract error code from returned sensor data
        :param sensor_data: Dictionary returned as current data
        """
        return sensor_data["status"]["Code"]

    @staticmethod
    def error_reason(sensor_data):
        """
        Extract error reason from returned sensor data
        :param sensor_data: Dictionary returned as current data
        """
        return sensor_data["status"]["Reason"]

    async def _current_data(self, fun, spec, spec_name, *spec_formattings):
        sensor = {}
        try:
            res = await self._fetch_solar_api(spec, spec_name, *spec_formattings)
        except InvalidAnswerError:
            # except if Host returns 404
            raise NotSupportedError(
                "Device type {} not supported by the fronius device".format(spec_name)
            )

        try:
            sensor.update(Fronius._status_data(res))
        except (TypeError, KeyError):
            raise InvalidAnswerError(
                "No header data returned from {} ({})".format(spec, spec_formattings)
            )
        else:
            if sensor["status"]["Code"] != 0:
                endpoint = spec[self.api_version]
                code = sensor["status"]["Code"]
                reason = sensor["status"]["Reason"]
                raise BadStatusError(endpoint, code, reason=reason, response=sensor)
        try:
            sensor.update(fun(res["Body"]["Data"]))
        except (TypeError, KeyError):
            # LoggerInfo oddly deviates from the default scheme
            try:
                sensor.update(fun(res["Body"]["LoggerInfo"]))
            except (TypeError, KeyError):
                raise InvalidAnswerError(
                    "No body data returned from {} ({})".format(spec, spec_formattings)
                )
        return sensor

    async def current_power_flow(self):
        """
        Get the current power flow of a smart meter system.
        """
        return await self._current_data(
            Fronius._system_power_flow, URL_POWER_FLOW, "current power flow"
        )

    async def current_system_meter_data(self):
        """
        Get the current meter data.
        """
        return await self._current_data(
            Fronius._system_meter_data, URL_SYSTEM_METER, "current system meter"
        )

    async def current_system_inverter_data(self):
        """
        Get the current inverter data.
        The values are provided as cumulated values and for each inverter
        """
        return await self._current_data(
            Fronius._system_inverter_data,
            URL_SYSTEM_INVERTER,
            "current system inverter",
        )

    async def current_system_ohmpilot_data(self):
        """
        Get the current ohmpilot data.
        """
        return await self._current_data(
            Fronius._system_ohmpilot_data,
            URL_SYSTEM_OHMPILOT,
            "current system ohmpilot",
        )

    async def current_meter_data(self, device: str = "0") -> Dict[str, Any]:
        """
        Get the current meter data for a device.
        """
        return await self._current_data(
            Fronius._device_meter_data, URL_DEVICE_METER, "current meter", device
        )

    async def current_storage_data(self, device: str = "0") -> Dict[str, Any]:
        """
        Get the current storage data for a device.
        Provides data about batteries.
        """
        return await self._current_data(
            Fronius._device_storage_data, URL_DEVICE_STORAGE, "current storage", device
        )

    async def current_system_storage_data(self):
        """
        Get the current storage data for a device.
        Provides data about batteries.
        """
        return await self._current_data(
            Fronius._system_storage_data, URL_SYSTEM_STORAGE, "current system storage"
        )

    async def current_inverter_data(self, device: str = "1") -> Dict[str, Any]:
        """
        Get the current inverter data of one device.
        """
        return await self._current_data(
            Fronius._device_inverter_data,
            URL_DEVICE_INVERTER_COMMON,
            "current inverter",
            device,
        )

    async def current_led_data(self):
        """
        Get the current info led data for all LEDs
        """
        return await self._current_data(
            Fronius._system_led_data, URL_SYSTEM_LED, "current led"
        )

    async def current_active_device_info(self):
        """
        Get info about the current active devices in a smart meter system.
        """
        return await self._current_data(
            Fronius._system_active_device_info,
            URL_ACTIVE_DEVICE_INFO_SYSTEM,
            "current active device info",
        )

    async def current_logger_info(self):
        """
        Get the current logger info of a smart meter system.
        """
        return await self._current_data(
            Fronius._logger_info, URL_LOGGER_INFO, "current logger info"
        )

    async def inverter_info(self):
        """
        Get the general infos of an inverter.
        """
        return await self._current_data(
            Fronius._inverter_info, URL_INVERTER_INFO, "inverter info"
        )

    @staticmethod
    def _system_led_data(data):
        _LOGGER.debug("Converting system led data: '{}'".format(data))
        sensor = {}

        _map = {
            "PowerLED": "power_led",
            "SolarNetLED": "solar_net_led",
            "SolarWebLED": "solar_web_led",
            "WLANLED": "wlan_led",
        }

        for led in _map:
            if led in data:
                sensor[_map[led]] = {
                    "color": data[led]["Color"],
                    "state": data[led]["State"],
                }

        return sensor

    @staticmethod
    def _system_power_flow(data):
        _LOGGER.debug("Converting system power flow data: '{}'".format(data))
        sensor = {}

        site = data["Site"]
        # Backwards compatability
        if data["Inverters"].get("1"):
            inverter = data["Inverters"]["1"]
            if "Battery_Mode" in inverter:
                sensor["battery_mode"] = {"value": inverter["Battery_Mode"]}
            if "SOC" in inverter:
                sensor["state_of_charge"] = {"value": inverter["SOC"], "unit": PERCENT}

        for index, inverter in enumerate(data["Inverters"]):
            if "Battery_Mode" in inverter:
                sensor["battery_mode_{}".format(index)] = {
                    "value": inverter["Battery_Mode"]
                }
            if "SOC" in inverter:
                sensor["state_of_charge_{}".format(index)] = {
                    "value": inverter["SOC"],
                    "unit": PERCENT,
                }

        if "BatteryStandby" in site:
            sensor["battery_standby"] = {"value": site["BatteryStandby"]}
        if "E_Day" in site:
            sensor["energy_day"] = {"value": site["E_Day"], "unit": WATT_HOUR}
        if "E_Total" in site:
            sensor["energy_total"] = {"value": site["E_Total"], "unit": WATT_HOUR}
        if "E_Year" in site:
            sensor["energy_year"] = {"value": site["E_Year"], "unit": WATT_HOUR}
        if "Meter_Location" in site:
            sensor["meter_location"] = {"value": site["Meter_Location"]}
        if "Mode" in site:
            sensor["meter_mode"] = {"value": site["Mode"]}
        if "P_Akku" in site:
            sensor["power_battery"] = {"value": site["P_Akku"], "unit": WATT}
        if "P_Grid" in site:
            sensor["power_grid"] = {"value": site["P_Grid"], "unit": WATT}
        if "P_Load" in site:
            sensor["power_load"] = {"value": site["P_Load"], "unit": WATT}
        if "P_PV" in site:
            sensor["power_photovoltaics"] = {"value": site["P_PV"], "unit": WATT}
        if "rel_Autonomy" in site:
            sensor["relative_autonomy"] = {
                "value": site["rel_Autonomy"],
                "unit": PERCENT,
            }
        if "rel_SelfConsumption" in site:
            sensor["relative_self_consumption"] = {
                "value": site["rel_SelfConsumption"],
                "unit": PERCENT,
            }

        return sensor

    @staticmethod
    def _system_meter_data(data):
        _LOGGER.debug("Converting system meter data: '{}'".format(data))

        sensor = {"meters": {}}

        for device_id, device_data in data.items():
            sensor["meters"][device_id] = Fronius._device_meter_data(device_data)

        return sensor

    @staticmethod
    def _system_inverter_data(data):
        _LOGGER.debug("Converting system inverter data: '{}'".format(data))
        sensor = {}

        sensor["energy_day"] = {"value": 0, "unit": WATT_HOUR}
        sensor["energy_total"] = {"value": 0, "unit": WATT_HOUR}
        sensor["energy_year"] = {"value": 0, "unit": WATT_HOUR}
        sensor["power_ac"] = {"value": 0, "unit": WATT}

        sensor["inverters"] = {}

        if "DAY_ENERGY" in data:
            for i in data["DAY_ENERGY"]["Values"]:
                sensor["inverters"][i] = {}
                sensor["inverters"][i]["energy_day"] = {
                    "value": data["DAY_ENERGY"]["Values"][i],
                    "unit": data["DAY_ENERGY"]["Unit"],
                }
                sensor["energy_day"]["value"] += data["DAY_ENERGY"]["Values"][i]
        if "TOTAL_ENERGY" in data:
            for i in data["TOTAL_ENERGY"]["Values"]:
                sensor["inverters"][i]["energy_total"] = {
                    "value": data["TOTAL_ENERGY"]["Values"][i],
                    "unit": data["TOTAL_ENERGY"]["Unit"],
                }
                sensor["energy_total"]["value"] += data["TOTAL_ENERGY"]["Values"][i]
        if "YEAR_ENERGY" in data:
            for i in data["YEAR_ENERGY"]["Values"]:
                sensor["inverters"][i]["energy_year"] = {
                    "value": data["YEAR_ENERGY"]["Values"][i],
                    "unit": data["YEAR_ENERGY"]["Unit"],
                }
                sensor["energy_year"]["value"] += data["YEAR_ENERGY"]["Values"][i]
        if "PAC" in data:
            for i in data["PAC"]["Values"]:
                sensor["inverters"][i]["power_ac"] = {
                    "value": data["PAC"]["Values"][i],
                    "unit": data["PAC"]["Unit"],
                }
                sensor["power_ac"]["value"] += data["PAC"]["Values"][i]

        return sensor

    @staticmethod
    def _device_ohmpilot_data(data):
        _LOGGER.debug("Converting ohmpilot data from '{}'".format(data))
        device = {}

        if "CodeOfError" in data:
            device["error_code"] = {"value": data["CodeOfError"]}

        if "CodeOfState" in data:
            state_code = data["CodeOfState"]
            device["state_code"] = {"value": state_code}
            device["state_message"] = {
                "value": OHMPILOT_STATE_CODES.get(state_code, "Unknown")
                }

        if "Details" in data:
            device["hardware"] = {"value": data["Details"]["Hardware"]}
            device["manufacturer"] = {"value": data["Details"]["Manufacturer"]}
            device["model"] = {"value": data["Details"]["Model"]}
            device["serial"] = {"value": data["Details"]["Serial"]}
            device["software"] = {"value": data["Details"]["Software"]}

        if "EnergyReal_WAC_Sum_Consumed" in data:
            device["energy_real_ac_consumed"] = {
                "value": data["EnergyReal_WAC_Sum_Consumed"], "unit": WATT_HOUR
                }

        if "PowerReal_PAC_Sum" in data:
            device["power_real_ac"] = {"value": data["PowerReal_PAC_Sum"], "unit": WATT}

        if "Temperature_Channel_1" in data:
            device["temperature_channel_1"] = {
                "value": data["Temperature_Channel_1"], "unit": DEGREE_CELSIUS
                }

        return device

    @staticmethod
    def _system_ohmpilot_data(data):
        _LOGGER.debug("Converting system ohmpilot data: '{}'".format(data))
        sensor = {"ohmpilots": {}}

        for device_id, device_data in data.items():
            sensor["ohmpilots"][device_id] = Fronius._device_ohmpilot_data(device_data)

        return sensor

    @staticmethod
    def _device_meter_data(data):
        _LOGGER.debug("Converting meter data: '{}'".format(data))

        meter = {}

        if "Current_AC_Phase_1" in data:
            meter["current_ac_phase_1"] = {
                "value": data["Current_AC_Phase_1"],
                "unit": AMPERE,
            }
        if "ACBRIDGE_CURRENT_ACTIVE_MEAN_01_F32" in data:
            meter["current_ac_phase_1"] = {
                "value": data["ACBRIDGE_CURRENT_ACTIVE_MEAN_01_F32"],
                "unit": AMPERE,
            }
        if "Current_AC_Phase_2" in data:
            meter["current_ac_phase_2"] = {
                "value": data["Current_AC_Phase_2"],
                "unit": AMPERE,
            }
        if "ACBRIDGE_CURRENT_ACTIVE_MEAN_02_F32" in data:
            meter["current_ac_phase_2"] = {
                "value": data["ACBRIDGE_CURRENT_ACTIVE_MEAN_02_F32"],
                "unit": AMPERE,
            }
        if "Current_AC_Phase_3" in data:
            meter["current_ac_phase_3"] = {
                "value": data["Current_AC_Phase_3"],
                "unit": AMPERE,
            }
        if "ACBRIDGE_CURRENT_ACTIVE_MEAN_03_F32" in data:
            meter["current_ac_phase_3"] = {
                "value": data["ACBRIDGE_CURRENT_ACTIVE_MEAN_03_F32"],
                "unit": AMPERE,
            }
        if "EnergyReactive_VArAC_Sum_Consumed" in data:
            meter["energy_reactive_ac_consumed"] = {
                "value": data["EnergyReactive_VArAC_Sum_Consumed"],
                "unit": VOLTAMPEREREACTIVE_HOUR,
            }
        if "EnergyReactive_VArAC_Sum_Produced" in data:
            meter["energy_reactive_ac_produced"] = {
                "value": data["EnergyReactive_VArAC_Sum_Produced"],
                "unit": VOLTAMPEREREACTIVE_HOUR,
            }
        if "EnergyReal_WAC_Minus_Absolute" in data:
            meter["energy_real_ac_minus"] = {
                "value": data["EnergyReal_WAC_Minus_Absolute"],
                "unit": WATT_HOUR,
            }
        if "EnergyReal_WAC_Plus_Absolute" in data:
            meter["energy_real_ac_plus"] = {
                "value": data["EnergyReal_WAC_Plus_Absolute"],
                "unit": WATT_HOUR,
            }
        if "EnergyReal_WAC_Sum_Consumed" in data:
            meter["energy_real_consumed"] = {
                "value": data["EnergyReal_WAC_Sum_Consumed"],
                "unit": WATT_HOUR,
            }
        if "SMARTMETER_ENERGYACTIVE_CONSUMED_SUM_F64" in data:
            meter["energy_real_consumed"] = {
                "value": data["SMARTMETER_ENERGYACTIVE_CONSUMED_SUM_F64"],
                "unit": WATT_HOUR,
            }
        if "EnergyReal_WAC_Sum_Produced" in data:
            meter["energy_real_produced"] = {
                "value": data["EnergyReal_WAC_Sum_Produced"],
                "unit": WATT_HOUR,
            }
        if "SMARTMETER_ENERGYACTIVE_PRODUCED_SUM_F64" in data:
            meter["energy_real_produced"] = {
                "value": data["SMARTMETER_ENERGYACTIVE_PRODUCED_SUM_F64"],
                "unit": WATT_HOUR,
            }
        if "Frequency_Phase_Average" in data:
            meter["frequency_phase_average"] = {
                "value": data["Frequency_Phase_Average"],
                "unit": HERTZ,
            }
        if "PowerApparent_S_Phase_1" in data:
            meter["power_apparent_phase_1"] = {
                "value": data["PowerApparent_S_Phase_1"],
                "unit": VOLTAMPERE,
            }
        if "PowerApparent_S_Phase_2" in data:
            meter["power_apparent_phase_2"] = {
                "value": data["PowerApparent_S_Phase_2"],
                "unit": VOLTAMPERE,
            }
        if "PowerApparent_S_Phase_3" in data:
            meter["power_apparent_phase_3"] = {
                "value": data["PowerApparent_S_Phase_3"],
                "unit": VOLTAMPERE,
            }
        if "PowerApparent_S_Sum" in data:
            meter["power_apparent"] = {
                "value": data["PowerApparent_S_Sum"],
                "unit": VOLTAMPERE,
            }
        if "PowerFactor_Phase_1" in data:
            meter["power_factor_phase_1"] = {
                "value": data["PowerFactor_Phase_1"],
            }
        if "PowerFactor_Phase_2" in data:
            meter["power_factor_phase_2"] = {
                "value": data["PowerFactor_Phase_2"],
            }
        if "PowerFactor_Phase_3" in data:
            meter["power_factor_phase_3"] = {
                "value": data["PowerFactor_Phase_3"],
            }
        if "PowerFactor_Sum" in data:
            meter["power_factor"] = {"value": data["PowerFactor_Sum"]}
        if "PowerReactive_Q_Phase_1" in data:
            meter["power_reactive_phase_1"] = {
                "value": data["PowerReactive_Q_Phase_1"],
                "unit": VOLTAMPEREREACTIVE,
            }
        if "PowerReactive_Q_Phase_2" in data:
            meter["power_reactive_phase_2"] = {
                "value": data["PowerReactive_Q_Phase_2"],
                "unit": VOLTAMPEREREACTIVE,
            }
        if "PowerReactive_Q_Phase_3" in data:
            meter["power_reactive_phase_3"] = {
                "value": data["PowerReactive_Q_Phase_3"],
                "unit": VOLTAMPEREREACTIVE,
            }
        if "PowerReactive_Q_Sum" in data:
            meter["power_reactive"] = {
                "value": data["PowerReactive_Q_Sum"],
                "unit": VOLTAMPEREREACTIVE,
            }
        if "PowerReal_P_Phase_1" in data:
            meter["power_real_phase_1"] = {
                "value": data["PowerReal_P_Phase_1"],
                "unit": WATT,
            }
        if "SMARTMETER_POWERACTIVE_01_F64" in data:
            meter["power_real_phase_1"] = {
                "value": data["SMARTMETER_POWERACTIVE_01_F64"],
                "unit": WATT,
            }
        if "PowerReal_P_Phase_2" in data:
            meter["power_real_phase_2"] = {
                "value": data["PowerReal_P_Phase_2"],
                "unit": WATT,
            }
        if "SMARTMETER_POWERACTIVE_02_F64" in data:
            meter["power_real_phase_2"] = {
                "value": data["SMARTMETER_POWERACTIVE_02_F64"],
                "unit": WATT,
            }
        if "PowerReal_P_Phase_3" in data:
            meter["power_real_phase_3"] = {
                "value": data["PowerReal_P_Phase_3"],
                "unit": WATT,
            }
        if "SMARTMETER_POWERACTIVE_03_F64" in data:
            meter["power_real_phase_3"] = {
                "value": data["SMARTMETER_POWERACTIVE_03_F64"],
                "unit": WATT,
            }
        if "PowerReal_P_Sum" in data:
            meter["power_real"] = {"value": data["PowerReal_P_Sum"], "unit": WATT}
        if "Voltage_AC_Phase_1" in data:
            meter["voltage_ac_phase_1"] = {
                "value": data["Voltage_AC_Phase_1"],
                "unit": VOLT,
            }
        if "Voltage_AC_Phase_2" in data:
            meter["voltage_ac_phase_2"] = {
                "value": data["Voltage_AC_Phase_2"],
                "unit": VOLT,
            }
        if "Voltage_AC_Phase_3" in data:
            meter["voltage_ac_phase_3"] = {
                "value": data["Voltage_AC_Phase_3"],
                "unit": VOLT,
            }
        if "Voltage_AC_PhaseToPhase_12" in data:
            meter["voltage_ac_phase_to_phase_12"] = {
                "value": data["Voltage_AC_PhaseToPhase_12"],
                "unit": VOLT,
            }
        if "Voltage_AC_PhaseToPhase_23" in data:
            meter["voltage_ac_phase_to_phase_23"] = {
                "value": data["Voltage_AC_PhaseToPhase_23"],
                "unit": VOLT,
            }
        if "Voltage_AC_PhaseToPhase_31" in data:
            meter["voltage_ac_phase_to_phase_31"] = {
                "value": data["Voltage_AC_PhaseToPhase_31"],
                "unit": VOLT,
            }
        if "Meter_Location_Current" in data:
            meter["meter_location"] = {"value": data["Meter_Location_Current"]}
        if "Enable" in data:
            meter["enable"] = {"value": data["Enable"]}
        if "Visible" in data:
            meter["visible"] = {"value": data["Visible"]}
        if "Details" in data:
            meter["manufacturer"] = {"value": data["Details"]["Manufacturer"]}
            meter["model"] = {"value": data["Details"]["Model"]}
            meter["serial"] = {"value": data["Details"]["Serial"]}

        return meter

    @staticmethod
    def _device_storage_data(data):
        _LOGGER.debug("Converting storage data from '{}'".format(data))
        sensor = {}

        if "Controller" in data:
            controller = Fronius._controller_data(data["Controller"])
            sensor.update(controller)

        if "Modules" in data:
            sensor["modules"] = {}
            module_count = 0

            for module in data["Modules"]:
                sensor["modules"][module_count] = Fronius._module_data(module)
                module_count += 1

        return sensor

    @staticmethod
    def _system_storage_data(data):
        _LOGGER.debug("Converting system storage data: '{}'".format(data))

        sensor = {"storages": {}}

        for device_id, device_data in data.items():
            sensor["storages"][device_id] = Fronius._device_storage_data(device_data)

        return sensor

    @staticmethod
    def _device_inverter_data(data):
        _LOGGER.debug("Converting inverter data from '{}'".format(data))
        sensor = {}

        if "DAY_ENERGY" in data:
            sensor["energy_day"] = {
                "value": data["DAY_ENERGY"]["Value"],
                "unit": data["DAY_ENERGY"]["Unit"],
            }
        if "TOTAL_ENERGY" in data:
            sensor["energy_total"] = {
                "value": data["TOTAL_ENERGY"]["Value"],
                "unit": data["TOTAL_ENERGY"]["Unit"],
            }
        if "YEAR_ENERGY" in data:
            sensor["energy_year"] = {
                "value": data["YEAR_ENERGY"]["Value"],
                "unit": data["YEAR_ENERGY"]["Unit"],
            }
        if "FAC" in data:
            sensor["frequency_ac"] = {
                "value": data["FAC"]["Value"],
                "unit": data["FAC"]["Unit"],
            }
        if "IAC" in data:
            sensor["current_ac"] = {
                "value": data["IAC"]["Value"],
                "unit": data["IAC"]["Unit"],
            }
        if "IDC" in data:
            sensor["current_dc"] = {
                "value": data["IDC"]["Value"],
                "unit": data["IDC"]["Unit"],
            }
        if "IDC_2" in data:
            sensor["current_dc_2"] = {
                "value": data["IDC_2"]["Value"],
                "unit": data["IDC_2"]["Unit"],
            }
        if "PAC" in data:
            sensor["power_ac"] = {
                "value": data["PAC"]["Value"],
                "unit": data["PAC"]["Unit"],
            }
        if "UAC" in data:
            sensor["voltage_ac"] = {
                "value": data["UAC"]["Value"],
                "unit": data["UAC"]["Unit"],
            }
        if "UDC" in data:
            sensor["voltage_dc"] = {
                "value": data["UDC"]["Value"],
                "unit": data["UDC"]["Unit"],
            }
        if "UDC_2" in data:
            sensor["voltage_dc_2"] = {
                "value": data["UDC_2"]["Value"],
                "unit": data["UDC_2"]["Unit"],
            }
        if "DeviceStatus" in data:
            if "InverterState" in data["DeviceStatus"]:
                sensor["inverter_state"] = {
                    "value": data["DeviceStatus"]["InverterState"]
                }
            if "ErrorCode" in data["DeviceStatus"]:
                sensor["error_code"] = {"value": data["DeviceStatus"]["ErrorCode"]}
            if "StatusCode" in data["DeviceStatus"]:
                sensor["status_code"] = {"value": data["DeviceStatus"]["StatusCode"]}
            if "LEDState" in data["DeviceStatus"]:
                sensor["led_state"] = {"value": data["DeviceStatus"]["LEDState"]}
            if "LEDColor" in data["DeviceStatus"]:
                sensor["led_color"] = {"value": data["DeviceStatus"]["LEDColor"]}

        return sensor

    @staticmethod
    def _controller_data(data):

        controller = {}

        if "Capacity_Maximum" in data:
            controller["capacity_maximum"] = {
                "value": data["Capacity_Maximum"],
                "unit": "Ah",
            }
        if "DesignedCapacity" in data:
            controller["capacity_designed"] = {
                "value": data["DesignedCapacity"],
                "unit": "Ah",
            }
        if "Current_DC" in data:
            controller["current_dc"] = {"value": data["Current_DC"], "unit": AMPERE}
        if "Voltage_DC" in data:
            controller["voltage_dc"] = {"value": data["Voltage_DC"], "unit": VOLT}
        if "Voltage_DC_Maximum_Cell" in data:
            controller["voltage_dc_maximum_cell"] = {
                "value": data["Voltage_DC_Maximum_Cell"],
                "unit": VOLT,
            }
        if "Voltage_DC_Minimum_Cell" in data:
            controller["voltage_dc_minimum_cell"] = {
                "value": data["Voltage_DC_Minimum_Cell"],
                "unit": VOLT,
            }
        if "StateOfCharge_Relative" in data:
            controller["state_of_charge"] = {
                "value": data["StateOfCharge_Relative"],
                "unit": PERCENT,
            }
        if "Temperature_Cell" in data:
            controller["temperature_cell"] = {
                "value": data["Temperature_Cell"],
                "unit": DEGREE_CELSIUS,
            }
        if "Enable" in data:
            controller["enable"] = {"value": data["Enable"]}
        if "Details" in data:
            controller["manufacturer"] = {"value": data["Details"]["Manufacturer"]}
            controller["model"] = {"value": data["Details"]["Model"]}
            controller["serial"] = {"value": data["Details"]["Serial"]}

        return controller

    @staticmethod
    def _module_data(data):

        module = {}

        if "Capacity_Maximum" in data:
            module["capacity_maximum"] = {
                "value": data["Capacity_Maximum"],
                "unit": "Ah",
            }
        if "DesignedCapacity" in data:
            module["capacity_designed"] = {
                "value": data["DesignedCapacity"],
                "unit": "Ah",
            }
        if "Current_DC" in data:
            module["current_dc"] = {"value": data["Current_DC"], "unit": AMPERE}
        if "Voltage_DC" in data:
            module["voltage_dc"] = {"value": data["Voltage_DC"], "unit": VOLT}
        if "Voltage_DC_Maximum_Cell" in data:
            module["voltage_dc_maximum_cell"] = {
                "value": data["Voltage_DC_Maximum_Cell"],
                "unit": VOLT,
            }
        if "Voltage_DC_Minimum_Cell" in data:
            module["voltage_dc_minimum_cell"] = {
                "value": data["Voltage_DC_Minimum_Cell"],
                "unit": VOLT,
            }
        if "StateOfCharge_Relative" in data:
            module["state_of_charge"] = {
                "value": data["StateOfCharge_Relative"],
                "unit": PERCENT,
            }
        if "Temperature_Cell" in data:
            module["temperature_cell"] = {
                "value": data["Temperature_Cell"],
                "unit": DEGREE_CELSIUS,
            }
        if "Temperature_Cell_Maximum" in data:
            module["temperature_cell_maximum"] = {
                "value": data["Temperature_Cell_Maximum"],
                "unit": DEGREE_CELSIUS,
            }
        if "Temperature_Cell_Minimum" in data:
            module["temperature_cell_minimum"] = {
                "value": data["Temperature_Cell_Minimum"],
                "unit": DEGREE_CELSIUS,
            }
        if "CycleCount_BatteryCell" in data:
            module["cycle_count_cell"] = {"value": data["CycleCount_BatteryCell"]}
        if "Status_BatteryCell" in data:
            module["status_cell"] = {"value": data["Status_BatteryCell"]}
        if "Enable" in data:
            module["enable"] = {"value": data["Enable"]}
        if "Details" in data:
            module["manufacturer"] = {"value": data["Details"]["Manufacturer"]}
            module["model"] = {"value": data["Details"]["Model"]}
            module["serial"] = {"value": data["Details"]["Serial"]}

        return module

    @staticmethod
    def _system_active_device_info(data: dict):
        _LOGGER.debug("Converting system active device data: '{}'".format(data))
        sensor = {}

        if "Inverter" in data:
            inverters = []
            for device_id, device in data["Inverter"].items():
                inverter = {"device_id": device_id, "device_type": device["DT"]}
                if "Serial" in device:
                    inverter["serial_number"] = device["Serial"]
                inverters.append(inverter)
            sensor["inverters"] = inverters

        if "Meter" in data:
            meters = []
            for device_id, device in data["Meter"].items():
                meter = {"device_id": device_id}
                if "Serial" in device:
                    meter["serial_number"] = device["Serial"]
                meters.append(meter)
            sensor["meters"] = meters

        if "Ohmpilot" in data:
            ohmpilots = []
            for device_id, device in data["Ohmpilot"].items():
                ohmpilot = {"device_id": device_id}
                if "Serial" in device:
                    ohmpilot["serial_number"] = device["Serial"]
                ohmpilots.append(ohmpilot)
            sensor["ohmpilots"] = ohmpilots

        if "SensorCard" in data:
            sensor_cards = []
            for device_id, device in data["SensorCard"].items():
                sensor_card = {"device_id": device_id, "device_type": device["DT"]}
                if "Serial" in device:
                    sensor_card["serial_number"] = device["Serial"]
                sensor_card["channel_names"] = list(
                    map(lambda x: x.lower().replace(" ", "_"), device["ChannelNames"])
                )
                sensor_cards.append(sensor_card)
            sensor["sensor_cards"] = sensor_cards

        if "Storage" in data:
            storages = []
            for device_id, device in data["Storage"].items():
                storage = {"device_id": device_id}
                if "Serial" in device:
                    storage["serial_number"] = device["Serial"]
                storages.append(storage)
            sensor["storages"] = storages

        if "StringControl" in data:
            string_controls = []
            for device_id, device in data["StringControl"].items():
                string_control = {"device_id": device_id}
                if "Serial" in device:
                    string_control["serial_number"] = device["Serial"]
                string_controls.append(string_control)
            sensor["string_controls"] = string_controls

        return sensor

    @staticmethod
    def _inverter_info(data):
        """Parse inverter info."""
        _LOGGER.debug("Converting inverter info: '{}'".format(data))
        inverters = []
        for inverter_index, inverter_info in data.items():
            inverter = {
                "device_id": {"value": inverter_index},
                "device_type": {"value": inverter_info["DT"]},
                "pv_power": {"value": inverter_info["PVPower"], "unit": WATT},
                "status_code": {"value": inverter_info["StatusCode"]},
                "unique_id": {"value": inverter_info["UniqueID"]},
            }
            if inverter_info["DT"] in INVERTER_DEVICE_TYPE:
                # add manufacturer and model if known
                inverter["device_type"].update(
                    INVERTER_DEVICE_TYPE[inverter_info["DT"]]
                )
            # "CustomName" not available on API V0 so default to ""
            # html escaped by V1 Snap-In, UTF-8 by V1 Gen24
            if "CustomName" in inverter_info:
                inverter["custom_name"] = {
                    "value": unescape(inverter_info["CustomName"])
                }
            # "ErrorCode" not in V1-Gen24
            if "ErrorCode" in inverter_info:
                inverter["error_code"] = {"value": inverter_info["ErrorCode"]}
            # "Show" not in V0
            if "Show" in inverter_info:
                inverter["show"] = {"value": inverter_info["Show"]}
            inverters.append(inverter)
        return {"inverters": inverters}

    @staticmethod
    def _logger_info(data):
        _LOGGER.debug("Converting Logger info: '{}'".format(data))
        sensor = {}

        if "CO2Factor" in data and "CO2Unit" in data:
            sensor["co2_factor"] = {
                "value": data["CO2Factor"],
                "unit": PER_KILOWATTHOUR.format(data["CO2Unit"]),
            }

        if "CashFactor" in data and "CashCurrency" in data:
            # which unit does this have?
            sensor["cash_factor"] = {
                "value": data["CashFactor"],
                "unit": PER_KILOWATTHOUR.format(data["CashCurrency"]),
            }

        if "DeliveryFactor" in data and "CashCurrency" in data:
            # which unit does this have?
            sensor["delivery_factor"] = {
                "value": data["DeliveryFactor"],
                "unit": PER_KILOWATTHOUR.format(data["CashCurrency"]),
            }

        if "HWVersion" in data:
            sensor["hardware_version"] = {"value": data["HWVersion"]}

        if "SWVersion" in data:
            sensor["software_version"] = {"value": data["SWVersion"]}

        if "PlatformID" in data:
            sensor["hardware_platform"] = {"value": data["PlatformID"]}

        if "ProductID" in data:
            sensor["product_type"] = {"value": data["ProductID"]}

        if "TimezoneLocation" in data:
            sensor["time_zone_location"] = {"value": data["TimezoneLocation"]}

        if "TimezoneName" in data:
            sensor["time_zone"] = {"value": data["TimezoneName"]}

        if "UTCOffset" in data:
            sensor["utc_offset"] = {"value": data["UTCOffset"]}

        if "UniqueID" in data:
            sensor["unique_identifier"] = {"value": data["UniqueID"]}

        return sensor
