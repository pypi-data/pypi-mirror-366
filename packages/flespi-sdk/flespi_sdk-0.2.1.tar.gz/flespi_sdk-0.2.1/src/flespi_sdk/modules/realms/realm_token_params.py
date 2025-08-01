from aiohttp import ClientSession

from flespi_sdk.base.flespi_session import FlespiSession


class RealmTokenParams(FlespiSession):
    def __init__(self, realm_id: int, session: ClientSession, operate_as: int):
        super().__init__(session=session, operate_as=operate_as)
        self.realm_id = realm_id

    async def get(self):
        params = {"fields": "token_params"}
        async with self.session.get(
            f"platform/realms/{self.realm_id}",
            params=params,
            headers=self.get_headers(),
        ) as response:
            return (await self.get_result(response))[0]["token_params"]

    async def set(self, data: dict):
        response = await self.session.put(
            f"platform/realms/{self.realm_id}",
            json={"token_params": data},
            headers=self.get_headers(),
        )
        return await self.get_result(response)

    async def set_ttl(self, seconds: int):
        token_params = await self.get()
        if token_params["ttl"] == seconds:
            return
        token_params["ttl"] = seconds
        await self.set(token_params)

    async def set_ip_addresses(self, ip_addresses: list[str]):
        token_params = await self.get()
        ip_addresses_csv = ",".join(ip_addresses)
        if "ips" in token_params and token_params["ips"] == ip_addresses_csv:
            return
        token_params["ips"] = ip_addresses_csv
        await self.set(token_params)

    async def allow_all_origins(self):
        token_params = await self.get()
        if "origins" in token_params and token_params["origins"] == "*":
            return
        token_params["origins"] = "*"
        await self.set(token_params)

    async def set_origins(self, origins: list[str], allow_flespi_origins: bool = False):
        token_params = await self.get()
        token_params["origins"] = origins.copy()
        if allow_flespi_origins:
            token_params["origins"].append({"preset": "flespi"})
        await self.set(token_params)

    async def set_standard_access(self):
        token_params = await self.get()
        if token_params["access"]["type"] == 0:
            return
        token_params["access"] = {"type": 0}
        await self.set(token_params)

    async def set_master_access(self):
        token_params = await self.get()
        if token_params["access"]["type"] == 1:
            return
        token_params["access"] = {"type": 1}
        await self.set(token_params)

    async def set_acl_access(
        self, acl: list[dict] = [], templating: bool | None = None
    ):
        token_params = await self.get()
        access = {
            "type": 2,
            "acl": acl,
        }
        if templating is not None:
            access["templating"] = templating
        token_params["access"] = access
        await self.set(token_params)
