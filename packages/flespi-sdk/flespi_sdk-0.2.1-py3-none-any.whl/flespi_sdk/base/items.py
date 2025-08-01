import re
from typing import List
from aiohttp import ClientSession
from flespi_sdk.base.flespi_session import FlespiSession


class Items(FlespiSession):
    TOP_ITEMS = True

    def __init__(
        self,
        items_path: str,
        session: ClientSession,
        operate_as: int,
    ):
        super().__init__(session=session, operate_as=operate_as)
        self.items_path = items_path

    async def get(self, id: int, fields: list[str] = []):
        async with self.session.get(
            f"{self.items_path}/{id},cid={self.operate_as}",
            params=dict(fields=self._prepare_fields(fields)),
            headers=self.get_headers(),
        ) as response:
            results = await self.get_result(response)
            return self.construct_item(results[0])

    async def list(
        self, selector: str = "all", recursive: bool = False, fields: list[str] = []
    ):
        list_path = f"{self.items_path}/"
        if self.__class__.TOP_ITEMS and not recursive:
            if match := re.match("^{(.*)}$", selector):  # expression selector
                original_expression = match.group(1)
                list_path += f"{{{original_expression} && cid == {self.operate_as}}}"
            else:
                list_path += f"{selector},cid={self.operate_as}"
        else:
            list_path += selector

        async with self.session.get(
            list_path,
            params=dict(fields=self._prepare_fields(fields)),
            headers=self.get_headers(),
        ) as response:
            result = await self.get_result(response)
            return [self.construct_item(data) for data in result]

    def construct_item(self, _data: dict):
        raise NotImplementedError()

    def _prepare_fields(self, fields: List[str] = []):
        return ",".join(list(set(["id"] + fields)))
