# PyFronius - a very basic Fronius python bridge
[![Build Status](https://travis-ci.com/nielstron/pyfronius.svg?branch=master)](https://travis-ci.com/nielstron/pyfronius)
[![Coverage Status](https://coveralls.io/repos/github/nielstron/pyfronius/badge.svg?branch=master)](https://coveralls.io/github/nielstron/pyfronius?branch=master)
 [![PyPI version](https://badge.fury.io/py/PyFronius.svg)](https://pypi.org/project/pyfronius/)
 ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/PyFronius.svg)
 [![PyPI - Status](https://img.shields.io/pypi/status/PyFronius.svg)](https://pypi.org/project/pyfronius/)

A package that connects to a Fronius Symo device in the local network and provides data
that is provided via the JSON API of the Fronius Symo.
It is able to read the system and photovoltaic status.

The package supports the following data provided by fronius devices:

Power Flow (System)
Meter (System and Device Scope)
Inverter (System and Device Scope)
Storage (Device Scope only) 

The api can be enlarged based on the official Fronius JSON API V1, pull requests are very welcome.
Further, currently supported API versions are [V1](https://www.fronius.com/~/downloads/Solar%20Energy/Operating%20Instructions/42%2C0410%2C2012.pdf)
and [V0](https://www.fronius.com/~/downloads/Solar%20Energy/Operating%20Instructions/42,0410,2011.pdf).

I also know there are better scripts, yet they are not on pypi which is necessary
for using them with [Home Assistant](https://www.home-assistant.io)
