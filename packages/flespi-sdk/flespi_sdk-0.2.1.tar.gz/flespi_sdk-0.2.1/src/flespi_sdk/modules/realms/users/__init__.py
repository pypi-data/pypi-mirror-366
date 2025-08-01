from aiohttp import ClientSession
from flespi_sdk.base.items import Items
from flespi_sdk.modules.realms.users.user import User


class Users(Items):
    TOP_ITEMS = False

    def __init__(
        self,
        realm_id: int,
        session: ClientSession,
        operate_as: int,
    ):
        """
        Initializes the RealmUsers class with a client instance.

        :param client: The client instance used to make API requests.
        """
        self.realm_id = realm_id
        super().__init__(
            items_path=f"/platform/realms/{realm_id}/users",
            session=session,
            operate_as=operate_as,
        )

    def construct_item(self, item: dict):
        return User(
            realm_id=self.realm_id,
            item=item,
            session=self.session,
            operate_as=self.operate_as,
        )
