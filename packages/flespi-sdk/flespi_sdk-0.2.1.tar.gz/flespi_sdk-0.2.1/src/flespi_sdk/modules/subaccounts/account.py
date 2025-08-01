from aiohttp import ClientSession

from flespi_sdk.modules.devices import Devices
from flespi_sdk.base.item import Item
from flespi_sdk.modules.mqtt import MQTT
from flespi_sdk.modules.realms import Realms
from flespi_sdk.modules.subaccounts import Subaccounts


class Account(Item):
    FIELDS = [
        "email",
        "counters",
        "blocked",
        "limit_id",
        "region",
        "created",
        "accessed",
        "enabled",
    ]

    def __init__(self, item: dict, session: ClientSession):
        account_id = item["id"]
        super().__init__(
            id=account_id,
            item_path="/platform/customer",
            session=session,
            operate_as=account_id,
        )

        self.subaccounts = Subaccounts(self.session, self.id)
        self.realms = Realms(self.session, self.id)
        self.devices = Devices(self.session, self.id)
        self.mqtt = MQTT(self.session, self.id)

        self.email = None
        self.counters = None
        self.blocked = None
        self.limit_id = None
        self.region = None
        self.enabled = None
        self.created = None
        self.accessed = None
        self._update_fields(item=item)

    async def stop(self) -> None:
        """
        Close the aiohttp session.
        """
        await self.session.close()
