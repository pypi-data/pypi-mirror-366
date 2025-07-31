import aiohttp

from flespi_sdk.base.items import Items
from flespi_sdk.modules.realms.realm import Realm


class Realms(Items):
    def __init__(self, session: aiohttp.ClientSession, operate_as: int):
        super().__init__(
            items_path="/platform/realms", session=session, operate_as=operate_as
        )

    def construct_item(self, item: dict):
        return Realm(
            item=item,
            session=self.session,
            operate_as=self.operate_as,
        )
