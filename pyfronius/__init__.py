'''
Created on 27.09.2017

@author: Niels
@author: Gerrit Beine
'''
import asyncio
import json
import logging

import async_timeout

_LOGGER = logging.getLogger(__name__)

URL_POWER_FLOW = "{}://{}/solar_api/v1/GetPowerFlowRealtimeData.fcgi"
URL_SYSTEM_METER = "{}://{}/solar_api/v1/GetMeterRealtimeData.cgi?Scope=System"
URL_SYSTEM_INVERTER = "{}://{}/solar_api/v1/GetInverterRealtimeData.cgi?Scope=System"
URL_DEVICE_METER = "{}://{}/solar_api/v1/GetMeterRealtimeData.cgi?Scope=Device&DeviceId={}"
URL_DEVICE_STORAGE = "{}://{}/solar_api/v1/GetStorageRealtimeData.cgi?Scope=Device&DeviceId={}"
URL_DEVICE_INVERTER_CUMULATIVE = "{}://{}/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceId={}&DataCollection=CumulationInverterData"
URL_DEVICE_INVERTER_COMMON = "{}://{}/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceId={}&DataCollection=CommonInverterData"

class Fronius:
    '''
    Interface to communicate with the Fronius Symo over http / JSON
    Attributes:
        session     The AIO session
        host        The ip/domain of the Fronius device
        useHTTPS    Use HTTPS instead of HTTP
    '''
    def __init__(self, session, host, useHTTPS = False):
        '''
        Constructor
        '''
        self._aio_session = session
        self.host = host
        if useHTTPS:
            self.protocol = "https"
        else:
            self.protocol = "http"
        
    @asyncio.coroutine
    def _fetch_json(self, url, params = None):
        headers = {'content-type': 'application/json'}
        with async_timeout.timeout(10):
            res = yield from self._aio_session.get(url, headers=headers, params=params)
            return (yield from res.json())
    
    @asyncio.coroutine
    def current_power_flow(self):
        '''
        Get the current power flow of a smart meter system.
        '''
        res = yield from self._fetch_json(URL_POWER_FLOW.format(self.protocol, self.host))
        _LOGGER.debug(res)

        site = res['Body']['Data']['Site'] # shortcut
        inverter = res['Body']['Data']['Inverters']['1'] # shortcut

        sensor = {}
        
        sensor['timestamp'] = { 'value': res['Head']['Timestamp'] }
        sensor['status'] = res['Head']['Status']
       
        if "Battery_Mode" in inverter:
            sensor['battery_mode'] = { 'value': inverter['Battery_Mode'] }
        if "SOC" in inverter:
            sensor['state_of_charge'] = { 'value': inverter['SOC'], 'unit' :"%" }

        if "BatteryStandby" in site:
            sensor['battery_standby'] = { 'value' : site['BatteryStandby'] }
        if "E_Day" in site:
            sensor['energy_day'] = { 'value': site['E_Day'], 'unit': "Wh" }
        if "E_Total" in site:
            sensor['energy_total'] = { 'value': site['E_Total'], 'unit': "Wh" }
        if "E_Year" in site:
            sensor['energy_year'] = { 'value': site['E_Year'], 'unit': "Wh" }
        if "Meter_Location" in site:
            sensor['meter_location'] = { 'value': site['Meter_Location'] }
        if "Mode" in site:
            sensor['meter_mode'] = { 'value': site['Mode'] }
        if "P_Akku" in site:
            sensor['power_battery'] = { 'value': site['P_Akku'], 'unit': "W" }
        if "P_Grid" in site:
            sensor['power_grid'] = { 'value': site['P_Grid'], 'unit': "W" }
        if "P_Load" in site:
            sensor['power_load'] = { 'value': site['P_Load'], 'unit': "W" }
        if "P_PV" in site:
            sensor['power_photovoltaics'] = { 'value': site['P_PV'], 'unit': "W" }
        if "rel_Autonomy" in site:
            sensor['relative_autonomy'] = { 'value': site['rel_Autonomy'], 'unit': "%" }
        if "rel_SelfConsumption" in site:
            sensor['relative_self_consumption'] = { 'value': site['rel_SelfConsumption'], 'unit': "%" }

        return sensor
    
    @asyncio.coroutine
    def current_system_meter_data(self):
        '''
        Get the current meter data.
        '''
        res = yield from self._fetch_json(URL_SYSTEM_METER.format(self.protocol, self.host))
        _LOGGER.debug(res)

        data = res['Body']['Data'] # shortcut

        sensor = {}
        
        sensor['timestamp'] = { 'value': res['Head']['Timestamp'] }
        sensor['status'] = res['Head']['Status']

        sensor['meters'] = { }

        for i in data:
            sensor['meters'][i] = self._meter_data(data[i])

        return sensor

    @asyncio.coroutine
    def current_system_inverter_data(self):
        '''
        Get the current inverter data.
        The values are provided as cumulated values and for each inverter
        '''
        res = yield from self._fetch_json(URL_SYSTEM_INVERTER.format(self.protocol, self.host))
        _LOGGER.debug(res)

        data = res['Body']['Data'] # shortcut

        sensor = {}
        
        sensor['timestamp'] = { 'value': res['Head']['Timestamp'] }
        sensor['status'] = res['Head']['Status']
        sensor['energy_day'] = { 'value': 0, 'unit': "Wh" }
        sensor['energy_total'] = { 'value': 0, 'unit': "Wh" }
        sensor['energy_year'] = { 'value': 0, 'unit': "Wh" }
        sensor['power_ac'] = { 'value': 0, 'unit': "W" }

        sensor['inverters'] = {}
        
        if "DAY_ENERGY" in data:
            for i in data['DAY_ENERGY']['Values']:
                sensor['inverters'][i] = { }
                sensor['inverters'][i]['energy_day'] = { 'value': data['DAY_ENERGY']['Values'][i], 'unit': data['DAY_ENERGY']['Unit'] }
                sensor['energy_day']['value'] += data['DAY_ENERGY']['Values'][i]
        if "TOTAL_ENERGY" in data:
            for i in data['TOTAL_ENERGY']['Values']:
                sensor['inverters'][i]['energy_total'] = { 'value': data['TOTAL_ENERGY']['Values'][i], 'unit': data['TOTAL_ENERGY']['Unit'] }
                sensor['energy_total']['value'] += data['TOTAL_ENERGY']['Values'][i]
        if "YEAR_ENERGY" in data:
            for i in data['YEAR_ENERGY']['Values']:
                sensor['inverters'][i]['energy_year'] = { 'value': data['YEAR_ENERGY']['Values'][i], 'unit': data['TOTAL_ENERGY']['Unit'] }
                sensor['energy_year']['value'] += data['YEAR_ENERGY']['Values'][i]
        if "PAC" in data:
            for i in data['PAC']['Values']:
                sensor['inverters'][i]['power_ac'] = { 'value': data['PAC']['Values'][i], 'unit': data['TOTAL_ENERGY']['Unit'] }
                sensor['power_ac']['value'] += data['PAC']['Values'][i]

        return sensor

    @asyncio.coroutine
    def current_meter_data(self, device = 0):
        '''
        Get the current meter data for a device.
        '''
        res = yield from self._fetch_json(URL_DEVICE_METER.format(self.protocol, self.host, device))
        _LOGGER.debug(res)

        data = res['Body']['Data'] # shortcut

        sensor = {}
        
        sensor['timestamp'] = { 'value': res['Head']['Timestamp'] }
        sensor['status'] = res['Head']['Status']

        sensor.update(self._meter_data(data))
        
        return sensor

    @asyncio.coroutine
    def current_storage_data(self, device = 0):
        '''
        Get the current storage data for a device.
        '''
        res = yield from self._fetch_json(URL_DEVICE_STORAGE.format(self.protocol, self.host, device))
        _LOGGER.debug(res)


        sensor = { }
        
        sensor['timestamp'] = { 'value': res['Head']['Timestamp'] }
        sensor['status'] = res['Head']['Status']
        sensor['modules'] = { }

        if 'Controller' in res['Body']['Data']:

            controller = res['Body']['Data']['Controller'] # shortcut

            if "Capacity_Maximum" in controller:
                sensor['capacity_maximum'] = { 'value': controller['Capacity_Maximum'], 'unit': "Ah" }
            if "DesignedCapacity" in controller:
                sensor['capacity_designed'] = { 'value': controller['DesignedCapacity'], 'unit': "Ah" }
            if "Current_DC" in controller:
                sensor['current_dc'] = { 'value': controller['Current_DC'], 'unit': "A" }
            if "Voltage_DC" in controller:
                sensor['voltage_dc'] = { 'value': controller['Voltage_DC'], 'unit': "V" }
            if "Voltage_DC_Maximum_Cell" in controller:
                sensor['voltage_dc_maximum_cell'] = { 'value': controller['Voltage_DC_Maximum_Cell'], 'unit': "V" }
            if "Voltage_DC_Minimum_Cell" in controller:
                sensor['voltage_dc_minimum_cell'] = { 'value': controller['Voltage_DC_Minimum_Cell'], 'unit': "V" }
            if "StateOfCharge_Relative" in controller:
                sensor['state_of_charge'] = { 'value': controller['StateOfCharge_Relative'], 'unit': "%" }
            if "Temperature_Cell" in controller:
                sensor['temperature_cell'] = { 'value': controller['Temperature_Cell'], 'unit': "C" }
            if "Enable" in controller:
                sensor['enable'] = { 'value': controller['Enable'] }
            if "Details" in controller:
                sensor['manufacturer'] = { 'value': controller['Details']['Manufacturer'] }
                sensor['model'] = { 'value': controller['Details']['Model'] }
                sensor['serial'] = { 'value': controller['Details']['Serial'] }

        if 'Modules' in res['Body']['Data']:

            modules = res['Body']['Data']['Modules'] # shortcut
            module_count = 0;

            for data in modules:
                _LOGGER.debug(data)
                module = { }
            
                if "Capacity_Maximum" in data:
                    module['capacity_maximum'] = { 'value': data['Capacity_Maximum'], 'unit': "Ah" }
                if "DesignedCapacity" in data:
                    module['capacity_designed'] = { 'value': data['DesignedCapacity'], 'unit': "Ah" }
                if "Current_DC" in data:
                    module['current_dc'] = { 'value': data['Current_DC'], 'unit': "A" }
                if "Voltage_DC" in data:
                    module['voltage_dc'] = { 'value': data['Voltage_DC'], 'unit': "V" }
                if "Voltage_DC_Maximum_Cell" in data:
                    module['voltage_dc_maximum_cell'] = { 'value': data['Voltage_DC_Maximum_Cell'], 'unit': "V" }
                if "Voltage_DC_Minimum_Cell" in data:
                    module['voltage_dc_minimum_cell'] = { 'value': data['Voltage_DC_Minimum_Cell'], 'unit': "V" }
                if "StateOfCharge_Relative" in data:
                    module['state_of_charge'] = { 'value': data['StateOfCharge_Relative'], 'unit': "%" }
                if "Temperature_Cell" in data:
                    module['temperature_cell'] = { 'value': data['Temperature_Cell'], 'unit': "C" }
                if "Temperature_Cell_Maximum" in data:
                    module['temperature_cell_maximum'] = { 'value': data['Temperature_Cell_Maximum'], 'unit': "C" }
                if "Temperature_Cell_Minimum" in data:
                    module['temperature_cell_minimum'] = { 'value': data['Temperature_Cell_Minimum'], 'unit': "C" }
                if "CycleCount_BatteryCell" in data:
                    module['cycle_count_cell'] = { 'value': data['CycleCount_BatteryCell'] }
                if "Status_BatteryCell" in data:
                    module['status_cell'] = { 'value': data['Status_BatteryCell'] }
                if "Enable" in data:
                    module['enable'] = { 'value': data['Enable'] }
                if "Details" in data:
                    module['manufacturer'] = { 'value': data['Details']['Manufacturer'] }
                    module['model'] = { 'value': data['Details']['Model'] }
                    module['serial'] = { 'value': data['Details']['Serial'] }
                
                sensor['modules'][module_count] = module
            
                module_count += 1

        return sensor

    @asyncio.coroutine
    def current_inverter_data(self, device = 1):
        '''
        Get the current inverter data of one device.
        '''
        res = yield from self._fetch_json(URL_DEVICE_INVERTER_COMMON.format(self.protocol, self.host, device))
        _LOGGER.debug(res)

        data = res['Body']['Data'] # shortcut

        sensor = {}
        
        sensor['timestamp'] = { 'value': res['Head']['Timestamp'] }
        sensor['status'] = res['Head']['Status']

        if "DAY_ENERGY" in data:
            sensor['energy_day'] = { 'value': data['DAY_ENERGY']['Value'], 'unit': data['DAY_ENERGY']['Unit'] }
        if "TOTAL_ENERGY" in data:
            sensor['energy_total'] = { 'value': data['TOTAL_ENERGY']['Value'], 'unit': data['TOTAL_ENERGY']['Unit'] }
        if "YEAR_ENERGY" in data:
            sensor['energy_year'] = { 'value': data['YEAR_ENERGY']['Value'], 'unit': data['YEAR_ENERGY']['Unit'] }
        if "FAC" in data:
            sensor['frequency_ac'] = { 'value': data['FAC']['Value'], 'unit': data['FAC']['Unit'] }
        if "IAC" in data:
            sensor['current_ac'] = { 'value': data['IAC']['Value'], 'unit': data['IAC']['Unit'] }
        if "IDC" in data:
            sensor['current_dc'] = { 'value': data['IDC']['Value'], 'unit': data['IDC']['Unit'] }
        if "PAC" in data:
            sensor['power_ac'] = { 'value': data['PAC']['Value'], 'unit': data['PAC']['Unit'] }
        if "UAC" in data:
            sensor['voltage_ac'] = { 'value': data['UAC']['Value'], 'unit': data['UAC']['Unit'] }
        if "UDC" in data:
            sensor['voltage_dc'] = { 'value': data['UDC']['Value'], 'unit': data['UDC']['Unit'] }

        return sensor
 
    def _meter_data(self, data):
        
        sensor = { }
        
        if "Current_AC_Phase_1" in data:
            sensor['current_ac_phase_1'] = { 'value': data['Current_AC_Phase_1'], 'unit': "A" }
        if "Current_AC_Phase_2" in data:
            sensor['current_ac_phase_2'] = { 'value': data['Current_AC_Phase_2'], 'unit': "A" }
        if "Current_AC_Phase_3" in data:
            sensor['current_ac_phase_3'] = { 'value': data['Current_AC_Phase_3'], 'unit': "A" }
        if "EnergyReactive_VArAC_Sum_Consumed" in data:
            sensor['energy_reactive_ac_consumed'] = { 'value': data['EnergyReactive_VArAC_Sum_Consumed'], 'unit': "Wh" }
        if "EnergyReactive_VArAC_Sum_Produced" in data:
            sensor['energy_reactive_ac_produced'] = { 'value': data['EnergyReactive_VArAC_Sum_Produced'], 'unit': "Wh" }
        if "EnergyReal_WAC_Minus_Absolute" in data:
            sensor['energy_real_ac_minus'] = { 'value': data['EnergyReal_WAC_Minus_Absolute'], 'unit': "Wh" }
        if "EnergyReal_WAC_Plus_Absolute" in data:
            sensor['energy_real_ac_plus'] = { 'value': data['EnergyReal_WAC_Plus_Absolute'], 'unit': "Wh" }
        if "EnergyReal_WAC_Sum_Consumed" in data:
            sensor['energy_real_consumed'] = { 'value': data['EnergyReal_WAC_Sum_Consumed'], 'unit': "Wh" }
        if "EnergyReal_WAC_Sum_Produced" in data:
            sensor['energy_real_produced'] = { 'value': data['EnergyReal_WAC_Sum_Produced'], 'unit': "Wh" }
        if "Frequency_Phase_Average" in data:
            sensor['frequency_phase_average'] = { 'value': data['Frequency_Phase_Average'], 'unit': "Hz" }
        if "PowerApparent_S_Phase_1" in data:
            sensor['power_apparent_phase_1'] = { 'value': data['PowerApparent_S_Phase_1'], 'unit': "W" }
        if "PowerApparent_S_Phase_2" in data:
            sensor['power_apparent_phase_2'] = { 'value': data['PowerApparent_S_Phase_2'], 'unit': "W" }
        if "PowerApparent_S_Phase_3" in data:
            sensor['power_apparent_phase_3'] = { 'value': data['PowerApparent_S_Phase_3'], 'unit': "W" }
        if "PowerApparent_S_Sum" in data:
            sensor['power_apparent'] = { 'value': data['PowerApparent_S_Sum'], 'unit': "W" }
        if "PowerFactor_Phase_1" in data:
            sensor['power_factor_phase_1'] = { 'value': data['PowerFactor_Phase_1'], 'unit': "W" }
        if "PowerFactor_Phase_2" in data:
            sensor['power_factor_phase_2'] = { 'value': data['PowerFactor_Phase_2'], 'unit': "W" }
        if "PowerFactor_Phase_3" in data:
            sensor['power_factor_phase_3'] = { 'value': data['PowerFactor_Phase_3'], 'unit': "W" }
        if "PowerFactor_Sum" in data:
            sensor['power_factor'] = { 'value': data['PowerFactor_Sum'], 'unit': "W" }
        if "PowerReactive_Q_Phase_1" in data:
            sensor['power_reactive_phase_1'] = { 'value': data['PowerReactive_Q_Phase_1'], 'unit': "W" }
        if "PowerReactive_Q_Phase_2" in data:
            sensor['power_reactive_phase_2'] = { 'value': data['PowerReactive_Q_Phase_2'], 'unit': "W" }
        if "PowerReactive_Q_Phase_3" in data:
            sensor['power_reactive_phase_3'] = { 'value': data['PowerReactive_Q_Phase_3'], 'unit': "W" }
        if "PowerReactive_Q_Sum" in data:
            sensor['power_reactive'] = { 'value': data['PowerReactive_Q_Sum'], 'unit': "W" }
        if "PowerReal_P_Phase_1" in data:
            sensor['power_real_phase_1'] = { 'value': data['PowerReal_P_Phase_1'], 'unit': "W" }
        if "PowerReal_P_Phase_2" in data:
            sensor['power_real_phase_2'] = { 'value': data['PowerReal_P_Phase_2'], 'unit': "W" }
        if "PowerReal_P_Phase_3" in data:
            sensor['power_real_phase_3'] = { 'value': data['PowerReal_P_Phase_3'], 'unit': "W" }
        if "PowerReal_P_Sum" in data:
            sensor['power_real'] = { 'value': data['PowerReal_P_Sum'], 'unit': "W" }
        if "Voltage_AC_Phase_1" in data:
            sensor['voltage_ac_phase_1'] = { 'value': data['Voltage_AC_Phase_1'], 'unit': "V" }
        if "Voltage_AC_Phase_2" in data:
            sensor['voltage_ac_phase_2'] = { 'value': data['Voltage_AC_Phase_2'], 'unit': "V" }
        if "Voltage_AC_Phase_3" in data:
            sensor['voltage_ac_phase_3'] = { 'value': data['Voltage_AC_Phase_3'], 'unit': "V" }
        if "Voltage_AC_PhaseToPhase_12" in data:
            sensor['voltage_ac_phase_to_phase_12'] = { 'value': data['Voltage_AC_PhaseToPhase_12'], 'unit': "V" }
        if "Voltage_AC_PhaseToPhase_23" in data:
            sensor['voltage_ac_phase_to_phase_23'] = { 'value': data['Voltage_AC_PhaseToPhase_23'], 'unit': "V" }
        if "Voltage_AC_PhaseToPhase_31" in data:
            sensor['voltage_ac_phase_to_phase_31'] = { 'value': data['Voltage_AC_PhaseToPhase_31'], 'unit': "V" }
        if "Meter_Location_Current" in data:
            sensor['meter_location'] = { 'value': data['Meter_Location_Current'] }
        if "Enable" in data:
            sensor['enable'] = { 'value': data['Enable'] }
        if "Visible" in data:
            sensor['visible'] = { 'value': data['Visible'] }
        if "Details" in data:
            sensor['manufacturer'] = { 'value': data['Details']['Manufacturer'] }
            sensor['model'] = { 'value': data['Details']['Model'] }
            sensor['serial'] = { 'value': data['Details']['Serial'] }
        
        return sensor
