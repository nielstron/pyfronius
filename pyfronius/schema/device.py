from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class Firmware(BaseModel):
    updateAvailable: bool | None
    installedVersion: str | None
    availableVersion: str | None


class Sensor(BaseModel):
    sensorType: str
    sensorName: str
    isActive: bool
    activationDate: datetime
    deactivationDate: Optional[datetime]


class DeviceMetaData(BaseModel):
    # inverter
    deviceType: str
    deviceId: str
    deviceName: str
    deviceManufacturer: str
    serialnumber: Optional[str]
    deviceTypeDetails: Optional[str]
    dataloggerId: str
    nodeType: Optional[str]
    numberMPPTrackers: Optional[int]
    numberPhases: Optional[int]
    peakPower: Optional[Any]
    nominalAcPower: Optional[float]
    firmware: Optional[Firmware]
    isActive: bool
    activationDate: datetime
    deactivationDate: Optional[datetime]
    # battery extras
    capacity: Optional[float]
    # sensor extras
    sensors: Optional[Sensor]
    # smart meter extras
    deviceCategory: Optional[str]
    deviceLocation: Optional[str]
    # EV charger extras
    isOnline: Optional[bool]
    # Data logger extras


class DevicesMetaData(BaseModel):
    devices: list[DeviceMetaData] | None
