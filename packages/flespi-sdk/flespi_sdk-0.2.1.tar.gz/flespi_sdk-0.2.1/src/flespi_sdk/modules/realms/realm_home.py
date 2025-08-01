from aiohttp import ClientSession
from flespi_sdk.base.flespi_session import FlespiSession


class RealmHome(FlespiSession):
    def __init__(
        self,
        realm_id: int,
        session: ClientSession,
        operate_as: int,
    ):
        super().__init__(session=session, operate_as=operate_as)
        self.realm_id = realm_id

    async def get(self):
        params = {"fields": "home"}
        async with self.session.get(
            f"/platform/realms/{self.realm_id}",
            params=params,
            headers=self.get_headers(),
        ) as response:
            result = await self.get_result(response)
            return result[0]["home"]

    async def set(self, data: dict):
        response = await self.session.put(
            f"/platform/realms/{self.realm_id}",
            json={"home": data},
            headers=self.get_headers(),
        )
        return await self.get_result(response)

    async def set_current_subaccount(self):
        data = {"type": 0}
        await self.set(data)

    async def set_existing_subaccount(self, subaccount_id: int):
        data = {"type": 1, "subaccount_id": subaccount_id}
        await self.set(data)

    async def set_create_new_subaccount(
        self, subaccount_id: int | None = None, limit_id: int | None = None
    ):
        data = {"type": 2}
        if subaccount_id:
            data["subaccount_id"] = subaccount_id
        if limit_id:
            data["limit_id"] = limit_id

        await self.set(data)
