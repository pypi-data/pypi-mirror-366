from aiohttp import ClientSession
from flespi_sdk.modules.devices.device import Device
from flespi_sdk.base.items import Items


class Devices(Items):
    def __init__(self, session: ClientSession, operate_as: int):
        super().__init__(
            items_path="/gw/devices",
            session=session,
            operate_as=operate_as,
        )

    def construct_item(self, item: dict):
        return Device(
            item=item,
            session=self.session,
            operate_as=self.operate_as,
        )
