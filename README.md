# PyFronius - a very basic Fronius python bridge

A package that connects to a Fronius Symo device in the local network and provides data
that is provided via the JSON API of the Fronius Symo.
It is able to read the system and photovoltaic status.

The api can be enlarged based on the official 
(Fronius JSON API V1)[https://www.fronius.com/~/downloads/Solar%20Energy/Operating%20Instructions/42%2C0410%2C2012.pdf],
 pull requests are very welcome.

I also know there are better scripts, yet they are not on pypi which is necessary
for using them with (Home Assistant)[https://www.home-assistant.io]