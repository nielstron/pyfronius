'''
Created on 27.09.2017

@author: Niels
'''
import json
import requests

def test_fronius(ip):
    '''
    Tests whether an Fronius answers under given ip and port
    Attributes:
        ip      IP of the Fronius
    '''
    if "http://" not in ip and "https://" not in ip:
        ip = "http://" + ip
    # load json data from delivered ip
    fronius_grid_json_path = "/components/5/0/?print=names"

    # if the below works we can be pretty sure there is a fronius answering
    try :
        # get data by JSON API
       
        r = requests.get(ip + fronius_grid_json_path)
            
        json_dict = json.loads(r.text)
        timestamp = json_dict['Body']['Data']['TimeStamp'];
        
        if timestamp is not None:
            return True
        return False
    except requests.exceptions.ConnectionError:
        return False
    except KeyError:
        return False

class Fronius(object):
    '''
    Interface to communicate with the Fronius Symo over http / JSON
    Attributes:
        ip         The ip/domain of the Fronius
    '''
    ip = ""

    def __init__(self, ip):
        '''
        Constructor
        '''
        if "http://" not in ip and "https://" not in ip:
            ip = "http://" + ip
        if ip[-1] == '/':
            del ip[-1]
        self.ip = ip
    
    def current_system_state(self):
        '''
        Crunch the latest data about the main system
        Returns a dict mapping each key name to value and unit
        '''
        # load json data from delivered ip
        fronius_grid_json_path = "/components/5/0/?print=names"
        # get data by JSON API
        r = requests.get(self.ip + fronius_grid_json_path)
        
        json_dict = json.loads(r.text)
        data = json_dict['Body']['Data']
        # Create a single sensor for every transmitted value.
        

        sensor_dict = {}
        for key in data.keys():
            sensor_dict.update(
                {str(key).lower() :
                [data[key]['value'],
                data[key]['unit']]})

        # handle null/None values
        
        # Self consumption is null when generated power is null,
        # so it should actually be equal to current grid / at 100%
        if sensor_dict['power_p_selfconsumption'] is None:
            # absolute self consumption = grid(2)"""
            sensor_dict['power_p_selfconsumption'] = sensor_dict[Power_P_Grid][0]
        if sensor_dict['relative_current_selfconsumption'] is None:
            # relative self consumption at 100
            sensor_dict['relative_current_selfconsumption'] = 100
        # every other value is 0 when null
        for key in [
            'relative_current_selfconsumption',
            'power_p_selfconsumption',
            'power_p_generate']:
            if sensor_dict[key] is None:
                sensor_dict[key] = 0
        
        return sensor_dict
    
    def current_pv_state(self):
        '''
        Crunch the latest data about the photovoltaic energy production
        Returns a list of parsed system data
        '''
        # load json data from delivered ip
        fronius_grid_json_path = \
            "/solar_api/v1/GetInverterRealtimeData.fcgi?Scope=System"
        # get data by JSON API
        r = requests.get(self.ip + fronius_grid_json_path)
        
        json_dict = json.loads(r.text)
        data = json_dict['Body']['Data']
        
        sensor_dict = {}
        for key in data.keys():
            sensor_dict.update(
                {str(key).lower() :
                [data[key]['Values']['1'],
                data[key]['Unit']]})

        
        return sensor_dict
        