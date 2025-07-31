from aiohttp import ClientSession
from flespi_sdk.base.item import Item


class User(Item):
    FIELDS = [
        "has_password",
        "subaccount_id",
        "token_params",
        "token_id",
        "token",
        "created",
    ]

    def __init__(
        self,
        realm_id: int,
        item: dict,
        session: ClientSession,
        operate_as: int,
    ):
        """
        Initializes the RealmUsers class with a client instance.

        :param client: The client instance used to make API requests.
        """
        user_id = item["id"]
        super().__init__(
            id=user_id,
            item_path=f"platform/realms/{realm_id}/users/{user_id}",
            session=session,
            operate_as=operate_as,
        )

        self.has_password = None
        self.subaccount_id = None
        self.token_params = None
        self.token_id = None
        self.token = None
        self.created = None
        self._update_fields(item=item)

    async def update_password(
        self,
        password: str,
    ) -> None:
        """
        Updates the password of the user.

        :param password: The new password for the user.
        """
        if len(password) < 16:
            raise ValueError("Password must be at least 16 characters long")

        async with self.session.put(
            self.item_path,
            json={"password": password},
            headers=self.get_headers(),
        ) as response:
            await self.get_result(response)
