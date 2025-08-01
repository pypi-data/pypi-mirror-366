from aiohttp import ClientSession

from flespi_sdk.modules.realms.realm_home import RealmHome
from flespi_sdk.modules.realms.realm_token_params import RealmTokenParams
from flespi_sdk.modules.realms.users import Users
from flespi_sdk.base.item import Item


class Realm(Item):
    """
    Represents a realm in the Flespi system.
    """

    FIELDS = [
        "public_id",
        "public_info",
        "blocked",
    ]

    def __init__(
        self,
        item: dict,
        session: ClientSession,
        operate_as: int,
    ):
        realm_id = item["id"]
        super().__init__(
            id=realm_id,
            item_path=f"platform/realms/{realm_id}",
            session=session,
            operate_as=operate_as,
        )
        self.users = Users(realm_id=realm_id, session=session, operate_as=operate_as)

        self.home = RealmHome(realm_id=realm_id, session=session, operate_as=operate_as)
        self.token_params = RealmTokenParams(
            realm_id=realm_id, session=session, operate_as=operate_as
        )

        self.public_id = None
        self.public_info = None
        self.blocked = None
        self._update_fields(item=item)
