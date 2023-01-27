# PyFronius - a very basic Fronius python bridge
[![Build Status](https://app.travis-ci.com/nielstron/pyfronius.svg?branch=master)](https://app.travis-ci.com/nielstron/pyfronius)
[![Coverage Status](https://coveralls.io/repos/github/nielstron/pyfronius/badge.svg?branch=master)](https://coveralls.io/github/nielstron/pyfronius?branch=master)
 [![PyPI version](https://badge.fury.io/py/PyFronius.svg)](https://pypi.org/project/pyfronius/)
 ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/PyFronius.svg)
 [![PyPI - Status](https://img.shields.io/pypi/status/PyFronius.svg)](https://pypi.org/project/pyfronius/)

A package that can connect to a Fronius device in the local network (provides data
that is provided via the JSON API of the Fronius) or via the cloud Solar Web api.
This includes the grid consumption, grid return, photovoltaic production
and many more details on the status of the local power supply.

## Local api Features 

The package supports the following data provided by Fronius devices:

- Power Flow (System scope)
- Meter (System and Device scope)
- Inverter (System and Device scope)
- Storage (System and Device scope, Experimental) 
- Active Devices
- Logger Information
- Inverter Information

The package currently supportes the Fronius API V1 and V0
and aims to support as many different device types as possible (Hybrid, GEN24,...).

I also know there are better scripts, yet they are not on pypi which is necessary
for using them with [Home Assistant](https://www.home-assistant.io)

## Cloud api Features

- Talks to your Fronius Solar.web PV system via Cloud API
- Automatic retries with exponential backoff
- Optionally pass in a `httpx` client

Although intended as a library a `cloud_example.py` is provided for testing purposes.

To provide authentication for the example is via environment variables, e.g. on nix systems:

```
export ACCESS_KEY_ID=FKIAFEF58CFEFA94486F9C804CF6077A01AB
export ACCESS_KEY_VALUE=47c076bc-23e5-4949-37a6-4bcfcf8d21d6
export PV_SYSTEM_ID=20bb600e-019b-4e03-9df3-a0a900cda689
```

## Contributing

Support may be enhanced based on the official documentation ([V1](https://www.fronius.com/~/downloads/Solar%20Energy/Operating%20Instructions/42%2C0410%2C2012.pdf), [V0](https://www.fronius.com/~/downloads/Solar%20Energy/Operating%20Instructions/42,0410,2011.pdf)).
Pull requests are very welcome.

If you own a Fronius device, feel free to provide us with raw data returned
by fetching the API endpoints manually.
Data from systems featuring Ohmpilots and Storages are much welcomed as we
have no data for testing these so far.

