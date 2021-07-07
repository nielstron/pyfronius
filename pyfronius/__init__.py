"""
Created on 27.09.2017

@author: Niels
@author: Gerrit Beine
"""

import asyncio

import aiohttp
import json
import logging
import enum

_LOGGER = logging.getLogger(__name__)


class API_VERSION(enum.Enum):
    value: int

    AUTO = -1
    V0 = 0
    V1 = 1


API_BASEPATHS = {
    API_VERSION.V0: "/solar_api/",
    API_VERSION.V1: "/solar_api/v1",
}

URL_API_VERSION = "solar_api/GetAPIVersion.cgi"
URL_POWER_FLOW = {API_VERSION.V1: "GetPowerFlowRealtimeData.fcgi"}
URL_SYSTEM_METER = {API_VERSION.V1: "GetMeterRealtimeData.cgi?Scope=System"}
URL_SYSTEM_INVERTER = {
    API_VERSION.V0: "GetInverterRealtimeData.cgi?Scope=System",
    API_VERSION.V1: "GetInverterRealtimeData.cgi?Scope=System",
}
URL_SYSTEM_LED = {API_VERSION.V1: "GetLoggerLEDInfo.cgi"}
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


class NotSupportedError(ValueError):
    """
    An error to be raised if a specific feature is not supported by the specified device
    """

    pass


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

    def __init__(self, session, url, api_version=API_VERSION.AUTO):
        """
        Constructor
        """
        self._aio_session = session
        self.url = url
        self.api_version = api_version
        self.base_url = API_BASEPATHS.get(API_VERSION)

    async def _fetch_json(self, url):
        """
        Fetch json value from fixed url
        """
        try:
            async with self._aio_session.get(url) as res:
                text = await res.text()
                text = json.loads(text)
        except aiohttp.ServerTimeoutError:
            raise ConnectionError(
                "Connection to Fronius device timed out at {}.".format(url)
            )
        except aiohttp.ClientError:
            raise ConnectionError(
                "Connection to Fronius device failed at {}.".format(url)
            )
        except json.JSONDecodeError:
            raise ValueError("Host returned a non-JSON reply at {}.".format(url))
        return text

    async def fetch_api_version(self):
        """
        Fetches the highest supported API version of the initiated fronius device
        :return:
        """
        try:
            res = await self._fetch_json("{}/{}".format(self.url, URL_API_VERSION))
            api_version, base_url = API_VERSION(res["APIVersion"]), res["BaseURL"]
        except ValueError:
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
            _LOGGER.warning(
                "API version {} does not support request of {} data".format(
                    self.api_version, spec_name
                )
            )
            return None
        if spec_formattings:
            spec_url = spec_url.format(*spec_formattings)

        _LOGGER.debug("Get {} data for {}".format(spec_name, spec_url))
        res = await self._fetch_json("{}{}{}".format(self.url, self.base_url, spec_url))
        return res

    async def fetch(
        self,
        power_flow=True,
        system_meter=True,
        system_inverter=True,
        device_meter=frozenset([0]),
        # storage is not necessarily supported by every fronius device
        device_storage=frozenset([0]),
        device_inverter=frozenset([1]),
        loop=None,
    ):
        requests = []
        if power_flow:
            requests.append(self.current_power_flow())
        if system_meter:
            requests.append(self.current_system_meter_data())
        if system_inverter:
            requests.append(self.current_system_inverter_data())
        for i in device_meter:
            requests.append(self.current_meter_data(i))
        for i in device_storage:
            requests.append(self.current_storage_data(i))
        for i in device_inverter:
            requests.append(self.current_inverter_data(i))

        responses = await asyncio.gather(*requests, loop=loop)
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
        except ValueError:
            # except if Host returns 404
            raise NotSupportedError(
                "Device type {} not supported by the fronius device".format(spec_name)
            )

        try:
            sensor.update(Fronius._status_data(res))
            # TODO use update here as well
            sensor = fun(sensor, res["Body"]["Data"])
        except (TypeError, KeyError):
            # break if Data is empty
            _LOGGER.info("No data returned from {}".format(spec))
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

    async def current_meter_data(self, device=0):
        """
        Get the current meter data for a device.
        """
        return await self._current_data(
            Fronius._device_meter_data, URL_DEVICE_METER, "current meter", device
        )

    async def current_storage_data(self, device=0):
        """
        Get the current storage data for a device.
        Provides data about batteries.
        """
        return await self._current_data(
            Fronius._device_storage_data, URL_DEVICE_STORAGE, "current storage", device
        )

    async def current_inverter_data(self, device=1):
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

    @staticmethod
    def _system_led_data(sensor, data):
        _LOGGER.debug("Converting system led data: '{}'".format(data))

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
    def _system_power_flow(sensor, data):
        _LOGGER.debug("Converting system power flow data: '{}'".format(data))

        site = data["Site"]
        # Backwards compatability
        if data["Inverters"].get("1"):
            inverter = data["Inverters"]["1"]
            if "Battery_Mode" in inverter:
                sensor["battery_mode"] = {"value": inverter["Battery_Mode"]}
            if "SOC" in inverter:
                sensor["state_of_charge"] = {"value": inverter["SOC"], "unit": "%"}

        for index, inverter in enumerate(data["Inverters"]):
            if "Battery_Mode" in inverter:
                sensor["battery_mode_{}".format(index)] = {
                    "value": inverter["Battery_Mode"]
                }
            if "SOC" in inverter:
                sensor["state_of_charge_{}".format(index)] = {
                    "value": inverter["SOC"],
                    "unit": "%",
                }

        if "BatteryStandby" in site:
            sensor["battery_standby"] = {"value": site["BatteryStandby"]}
        if "E_Day" in site:
            sensor["energy_day"] = {"value": site["E_Day"], "unit": "Wh"}
        if "E_Total" in site:
            sensor["energy_total"] = {"value": site["E_Total"], "unit": "Wh"}
        if "E_Year" in site:
            sensor["energy_year"] = {"value": site["E_Year"], "unit": "Wh"}
        if "Meter_Location" in site:
            sensor["meter_location"] = {"value": site["Meter_Location"]}
        if "Mode" in site:
            sensor["meter_mode"] = {"value": site["Mode"]}
        if "P_Akku" in site:
            sensor["power_battery"] = {"value": site["P_Akku"], "unit": "W"}
        if "P_Grid" in site:
            sensor["power_grid"] = {"value": site["P_Grid"], "unit": "W"}
        if "P_Load" in site:
            sensor["power_load"] = {"value": site["P_Load"], "unit": "W"}
        if "P_PV" in site:
            sensor["power_photovoltaics"] = {"value": site["P_PV"], "unit": "W"}
        if "rel_Autonomy" in site:
            sensor["relative_autonomy"] = {"value": site["rel_Autonomy"], "unit": "%"}
        if "rel_SelfConsumption" in site:
            sensor["relative_self_consumption"] = {
                "value": site["rel_SelfConsumption"],
                "unit": "%",
            }

        return sensor

    @staticmethod
    def _system_meter_data(sensor, data):
        _LOGGER.debug("Converting system meter data: '{}'".format(data))

        sensor["meters"] = {}

        for i in data:
            sensor["meters"][i] = Fronius._meter_data(data[i])

        return sensor

    @staticmethod
    def _system_inverter_data(sensor, data):
        _LOGGER.debug("Converting system inverter data: '{}'".format(data))

        sensor["energy_day"] = {"value": 0, "unit": "Wh"}
        sensor["energy_total"] = {"value": 0, "unit": "Wh"}
        sensor["energy_year"] = {"value": 0, "unit": "Wh"}
        sensor["power_ac"] = {"value": 0, "unit": "W"}

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
    def _device_meter_data(sensor, data):
        _LOGGER.debug("Converting meter data: '{}'".format(data))

        sensor.update(Fronius._meter_data(data))

        return sensor

    @staticmethod
    def _device_storage_data(sensor, data):
        _LOGGER.debug("Converting storage data from '{}'".format(data))

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
    def _device_inverter_data(sensor, data):
        _LOGGER.debug("Converting inverter data from '{}'".format(data))

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
            sensor["inverter_state"] = {"value": data["DeviceStatus"]["InverterState"]}

        return sensor

    @staticmethod
    def _meter_data(data):

        meter = {}

        if "Current_AC_Phase_1" in data:
            meter["current_ac_phase_1"] = {
                "value": data["Current_AC_Phase_1"],
                "unit": "A",
            }
        if "ACBRIDGE_CURRENT_ACTIVE_MEAN_01_F32" in data:
            meter["current_ac_phase_1"] = {
                "value": data["ACBRIDGE_CURRENT_ACTIVE_MEAN_01_F32"],
                "unit": "A",
            }
        if "Current_AC_Phase_2" in data:
            meter["current_ac_phase_2"] = {
                "value": data["Current_AC_Phase_2"],
                "unit": "A",
            }
        if "ACBRIDGE_CURRENT_ACTIVE_MEAN_02_F32" in data:
            meter["current_ac_phase_2"] = {
                "value": data["ACBRIDGE_CURRENT_ACTIVE_MEAN_02_F32"],
                "unit": "A",
            }
        if "Current_AC_Phase_3" in data:
            meter["current_ac_phase_3"] = {
                "value": data["Current_AC_Phase_3"],
                "unit": "A",
            }
        if "ACBRIDGE_CURRENT_ACTIVE_MEAN_03_F32" in data:
            meter["current_ac_phase_3"] = {
                "value": data["ACBRIDGE_CURRENT_ACTIVE_MEAN_03_F32"],
                "unit": "A",
            }
        if "EnergyReactive_VArAC_Sum_Consumed" in data:
            meter["energy_reactive_ac_consumed"] = {
                "value": data["EnergyReactive_VArAC_Sum_Consumed"],
                "unit": "Wh",
            }
        if "EnergyReactive_VArAC_Sum_Produced" in data:
            meter["energy_reactive_ac_produced"] = {
                "value": data["EnergyReactive_VArAC_Sum_Produced"],
                "unit": "Wh",
            }
        if "EnergyReal_WAC_Minus_Absolute" in data:
            meter["energy_real_ac_minus"] = {
                "value": data["EnergyReal_WAC_Minus_Absolute"],
                "unit": "Wh",
            }
        if "EnergyReal_WAC_Plus_Absolute" in data:
            meter["energy_real_ac_plus"] = {
                "value": data["EnergyReal_WAC_Plus_Absolute"],
                "unit": "Wh",
            }
        if "EnergyReal_WAC_Sum_Consumed" in data:
            meter["energy_real_consumed"] = {
                "value": data["EnergyReal_WAC_Sum_Consumed"],
                "unit": "Wh",
            }
        if "SMARTMETER_ENERGYACTIVE_CONSUMED_SUM_F64" in data:
            meter["energy_real_consumed"] = {
                "value": data["SMARTMETER_ENERGYACTIVE_CONSUMED_SUM_F64"],
                "unit": "Wh",
            }
        if "EnergyReal_WAC_Sum_Produced" in data:
            meter["energy_real_produced"] = {
                "value": data["EnergyReal_WAC_Sum_Produced"],
                "unit": "Wh",
            }
        if "SMARTMETER_ENERGYACTIVE_PRODUCED_SUM_F64" in data:
            meter["energy_real_produced"] = {
                "value": data["SMARTMETER_ENERGYACTIVE_PRODUCED_SUM_F64"],
                "unit": "Wh",
            }
        if "Frequency_Phase_Average" in data:
            meter["frequency_phase_average"] = {
                "value": data["Frequency_Phase_Average"],
                "unit": "Hz",
            }
        if "PowerApparent_S_Phase_1" in data:
            meter["power_apparent_phase_1"] = {
                "value": data["PowerApparent_S_Phase_1"],
                "unit": "W",
            }
        if "PowerApparent_S_Phase_2" in data:
            meter["power_apparent_phase_2"] = {
                "value": data["PowerApparent_S_Phase_2"],
                "unit": "W",
            }
        if "PowerApparent_S_Phase_3" in data:
            meter["power_apparent_phase_3"] = {
                "value": data["PowerApparent_S_Phase_3"],
                "unit": "W",
            }
        if "PowerApparent_S_Sum" in data:
            meter["power_apparent"] = {
                "value": data["PowerApparent_S_Sum"],
                "unit": "W",
            }
        if "PowerFactor_Phase_1" in data:
            meter["power_factor_phase_1"] = {
                "value": data["PowerFactor_Phase_1"],
                "unit": "W",
            }
        if "PowerFactor_Phase_2" in data:
            meter["power_factor_phase_2"] = {
                "value": data["PowerFactor_Phase_2"],
                "unit": "W",
            }
        if "PowerFactor_Phase_3" in data:
            meter["power_factor_phase_3"] = {
                "value": data["PowerFactor_Phase_3"],
                "unit": "W",
            }
        if "PowerFactor_Sum" in data:
            meter["power_factor"] = {"value": data["PowerFactor_Sum"], "unit": "W"}
        if "PowerReactive_Q_Phase_1" in data:
            meter["power_reactive_phase_1"] = {
                "value": data["PowerReactive_Q_Phase_1"],
                "unit": "W",
            }
        if "PowerReactive_Q_Phase_2" in data:
            meter["power_reactive_phase_2"] = {
                "value": data["PowerReactive_Q_Phase_2"],
                "unit": "W",
            }
        if "PowerReactive_Q_Phase_3" in data:
            meter["power_reactive_phase_3"] = {
                "value": data["PowerReactive_Q_Phase_3"],
                "unit": "W",
            }
        if "PowerReactive_Q_Sum" in data:
            meter["power_reactive"] = {
                "value": data["PowerReactive_Q_Sum"],
                "unit": "W",
            }
        if "PowerReal_P_Phase_1" in data:
            meter["power_real_phase_1"] = {
                "value": data["PowerReal_P_Phase_1"],
                "unit": "W",
            }
        if "SMARTMETER_POWERACTIVE_01_F64" in data:
            meter["power_real_phase_1"] = {
                "value": data["SMARTMETER_POWERACTIVE_01_F64"],
                "unit": "W",
            }
        if "PowerReal_P_Phase_2" in data:
            meter["power_real_phase_2"] = {
                "value": data["PowerReal_P_Phase_2"],
                "unit": "W",
            }
        if "SMARTMETER_POWERACTIVE_02_F64" in data:
            meter["power_real_phase_2"] = {
                "value": data["SMARTMETER_POWERACTIVE_02_F64"],
                "unit": "W",
            }
        if "PowerReal_P_Phase_3" in data:
            meter["power_real_phase_3"] = {
                "value": data["PowerReal_P_Phase_3"],
                "unit": "W",
            }
        if "SMARTMETER_POWERACTIVE_03_F64" in data:
            meter["power_real_phase_3"] = {
                "value": data["SMARTMETER_POWERACTIVE_03_F64"],
                "unit": "W",
            }
        if "PowerReal_P_Sum" in data:
            meter["power_real"] = {"value": data["PowerReal_P_Sum"], "unit": "W"}
        if "Voltage_AC_Phase_1" in data:
            meter["voltage_ac_phase_1"] = {
                "value": data["Voltage_AC_Phase_1"],
                "unit": "V",
            }
        if "Voltage_AC_Phase_2" in data:
            meter["voltage_ac_phase_2"] = {
                "value": data["Voltage_AC_Phase_2"],
                "unit": "V",
            }
        if "Voltage_AC_Phase_3" in data:
            meter["voltage_ac_phase_3"] = {
                "value": data["Voltage_AC_Phase_3"],
                "unit": "V",
            }
        if "Voltage_AC_PhaseToPhase_12" in data:
            meter["voltage_ac_phase_to_phase_12"] = {
                "value": data["Voltage_AC_PhaseToPhase_12"],
                "unit": "V",
            }
        if "Voltage_AC_PhaseToPhase_23" in data:
            meter["voltage_ac_phase_to_phase_23"] = {
                "value": data["Voltage_AC_PhaseToPhase_23"],
                "unit": "V",
            }
        if "Voltage_AC_PhaseToPhase_31" in data:
            meter["voltage_ac_phase_to_phase_31"] = {
                "value": data["Voltage_AC_PhaseToPhase_31"],
                "unit": "V",
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
            controller["current_dc"] = {"value": data["Current_DC"], "unit": "A"}
        if "Voltage_DC" in data:
            controller["voltage_dc"] = {"value": data["Voltage_DC"], "unit": "V"}
        if "Voltage_DC_Maximum_Cell" in data:
            controller["voltage_dc_maximum_cell"] = {
                "value": data["Voltage_DC_Maximum_Cell"],
                "unit": "V",
            }
        if "Voltage_DC_Minimum_Cell" in data:
            controller["voltage_dc_minimum_cell"] = {
                "value": data["Voltage_DC_Minimum_Cell"],
                "unit": "V",
            }
        if "StateOfCharge_Relative" in data:
            controller["state_of_charge"] = {
                "value": data["StateOfCharge_Relative"],
                "unit": "%",
            }
        if "Temperature_Cell" in data:
            controller["temperature_cell"] = {
                "value": data["Temperature_Cell"],
                "unit": "C",
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
            module["current_dc"] = {"value": data["Current_DC"], "unit": "A"}
        if "Voltage_DC" in data:
            module["voltage_dc"] = {"value": data["Voltage_DC"], "unit": "V"}
        if "Voltage_DC_Maximum_Cell" in data:
            module["voltage_dc_maximum_cell"] = {
                "value": data["Voltage_DC_Maximum_Cell"],
                "unit": "V",
            }
        if "Voltage_DC_Minimum_Cell" in data:
            module["voltage_dc_minimum_cell"] = {
                "value": data["Voltage_DC_Minimum_Cell"],
                "unit": "V",
            }
        if "StateOfCharge_Relative" in data:
            module["state_of_charge"] = {
                "value": data["StateOfCharge_Relative"],
                "unit": "%",
            }
        if "Temperature_Cell" in data:
            module["temperature_cell"] = {
                "value": data["Temperature_Cell"],
                "unit": "C",
            }
        if "Temperature_Cell_Maximum" in data:
            module["temperature_cell_maximum"] = {
                "value": data["Temperature_Cell_Maximum"],
                "unit": "C",
            }
        if "Temperature_Cell_Minimum" in data:
            module["temperature_cell_minimum"] = {
                "value": data["Temperature_Cell_Minimum"],
                "unit": "C",
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
