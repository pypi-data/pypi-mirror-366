import aiohttp

from flespi_sdk.base.items import Items


class Subaccounts(Items):
    def __init__(self, session: aiohttp.ClientSession, operate_as: int):
        super().__init__(
            items_path="/platform/subaccounts", session=session, operate_as=operate_as
        )

    def construct_item(self, item: dict):
        from flespi_sdk.modules.subaccounts.account import Account

        return Account(
            item=item,
            session=self.session,
        )
