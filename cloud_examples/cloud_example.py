import asyncio
from pydantic import BaseSettings, SecretStr
from .cloud_api import Fronius_Solarweb


class AuthDetails(BaseSettings):
    ACCESS_KEY_ID: SecretStr
    ACCESS_KEY_VALUE: SecretStr
    PV_SYSTEM_ID: str


async def main():
    creds = AuthDetails()
    fronius = Fronius_Solarweb(
        access_key_id=creds.ACCESS_KEY_ID.get_secret_value(),
        access_key_value=creds.ACCESS_KEY_VALUE.get_secret_value(),
        pv_system_id=creds.PV_SYSTEM_ID,
    )

    print("Getting PV system meta data for ", creds.PV_SYSTEM_ID)
    pv_system_data = await fronius.get_pvsystem_meta_data()
    print(pv_system_data)

    print("Getting Devices meta data")
    devices_data = await fronius.get_devices_meta_data()
    print(devices_data)

    print("Getting power flow data")
    flow_data = await fronius.get_system_flow_data()
    print(flow_data)


if __name__ == "__main__":
    asyncio.run(main())
