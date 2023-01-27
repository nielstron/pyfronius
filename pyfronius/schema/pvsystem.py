from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class Address(BaseModel):
    street: str | None
    zipCode: str | None
    city: str | None
    state: str | None
    country: str | None


class Status(BaseModel):
    isOnline: bool
    battMode: Optional[str]


class PvSystemMetaData(BaseModel):
    pvSystemId: str
    name: str
    address: Address
    timezone: Optional[datetime]
    pictureURL: str
    peakPower: float
    meteoData: str | None
    lastImport: datetime
    installationDate: datetime


class PvSystemFlowData(BaseModel):
    pvSystemId: str
    status: Optional[Status]
    address: Optional[Address]
    timezone: Optional[datetime]
    pictureURL: Optional[str]
    peakPower: Optional[float]
    meteoData: str | None
    lastImport: Optional[datetime]
    installationDate: Optional[datetime]


class Channel(BaseModel):
    channelName: str
    channelType: str
    unit: str
    value: Any


class Data(BaseModel):
    logDateTime: datetime
    channels: Channel
