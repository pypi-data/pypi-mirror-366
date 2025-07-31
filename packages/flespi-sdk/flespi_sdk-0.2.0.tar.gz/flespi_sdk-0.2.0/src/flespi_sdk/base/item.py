from aiohttp import ClientSession
from flespi_sdk.base.flespi_session import FlespiSession


class Item(FlespiSession):
    COMMON_FIELDS: list[str] = ["name", "metadata", "cid"]
    FIELDS: list[str] = []

    def __init__(
        self,
        id: int,
        item_path: str,
        session: ClientSession,
        operate_as: int,
    ):
        super().__init__(session=session, operate_as=operate_as)
        self.id = id
        self.item_path = item_path

        self.name = None
        self.metadata = None
        self.cid = None

    async def get_field(self, field: str):
        item = await self.get_fields([field])
        return item.get(field)

    async def get_name(self):
        return await self.get_field("name")

    async def get_metadata(self) -> dict | None:
        self.metadata = await self.get_field("metadata")
        return self.metadata

    async def set_metadata(self, metadata: dict) -> None:
        """ "
        "Set metadata for the current account.
        :param metadata: Metadata as a dictionary.
        """
        async with self.session.put(
            self.item_path,
            json={"metadata": metadata},
            headers=self.get_headers(),
        ) as response:
            await self.get_result(response)

    async def get_metadata_value(
        self, key_path: str, default_value=None, ignore_cache: bool = False
    ):
        """
        Get a specific value from the metadata.
        :param key_path: The key path to the value in the metadata.
        :return: The value from the metadata.
        """
        metadata = self.metadata
        if ignore_cache:
            metadata = await self.get_metadata()

        if not metadata:
            return default_value
        keys = key_path.split(".")
        value = metadata
        for key in keys:
            if key in value:
                value = value[key]
            else:
                return default_value
        return value

    async def set_metadata_value(self, key_path: str, value) -> None:
        """
        Set a specific value in the metadata.
        :param key_path: The key path to the value in the metadata.
        :param value: The value to set.
        """
        metadata = await self.get_metadata() or {}
        keys = key_path.split(".")
        metadata_level = metadata
        for key in keys[:-1]:
            if key not in metadata_level:
                metadata_level[key] = {}
            metadata_level = metadata_level[key]
        metadata_level[keys[-1]] = value
        await self.set_metadata(metadata=metadata)

    async def delete_metadata_value(self, key_path: str) -> None:
        """
        Delete a specific key from the metadata.
        :param key_path: The key path to the value in the metadata.
        """
        metadata = await self.get_metadata()
        if not metadata:
            return
        keys = key_path.split(".")
        metadata_level = metadata
        for key in keys[:-1]:
            if key in metadata_level:
                metadata_level = metadata_level[key]
            else:
                return None
        del metadata_level[keys[-1]]
        await self.set_metadata(metadata=metadata)

    async def get_fields(self, fields: list[str]) -> dict:
        async with self.session.get(
            self.item_path,
            params=dict(fields=",".join(fields)),
            headers=self.get_headers(),
        ) as response:
            result = await self.get_result(response)
            item = result[0]
            self._update_fields(item)
            return item

    def _update_fields(self, item):
        for field, value in item.items():
            if field in self.COMMON_FIELDS or field in self.__class__.FIELDS:
                setattr(self, field, value)
