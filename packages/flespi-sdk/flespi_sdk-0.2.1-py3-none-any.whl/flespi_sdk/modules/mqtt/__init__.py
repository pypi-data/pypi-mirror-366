from typing import List
import urllib.parse

import aiohttp
from flespi_sdk.base.flespi_session import FlespiSession


class MQTT(FlespiSession):
    DEFAULT_MESSAGE_FIELDS = "cid,topic,payload,user_properties"

    def __init__(self, session: aiohttp.ClientSession, operate_as: int):
        super().__init__(session=session, operate_as=operate_as)

    async def list(self, topic: str, recursive: bool = False, fields: list[str] = []):
        """
        Get messages from the specified MQTT topic.
        :param topic: The MQTT topic to get messages from.
        :return: List of messages from the specified topic.
        """
        params = {"fields": ",".join(fields) if fields else self.DEFAULT_MESSAGE_FIELDS}
        list_path = f"/mqtt/messages/{urllib.parse.quote_plus(topic)}"
        if not recursive:
            list_path += f",cid={self.operate_as}"
        async with self.session.get(
            list_path,
            params=params,
            headers=self.get_headers(),
        ) as response:
            return await self.get_result(response)

    async def get(self, topic: str, fields: List[str] = []):
        """
        Get a specific message from the specified MQTT topic.
        :param topic: The MQTT topic to get the message from.
        :return: The message from the specified topic.
        """
        msgs = await self.list(topic=topic, fields=fields)
        if len(msgs) > 1:
            raise ValueError(
                f"Multiple messages found for topic '{topic}'. Use list() to get all messages."
            )
        elif len(msgs) == 0:
            raise ValueError(f"No messages found for topic '{topic}'.")
        else:
            return msgs[0]

    async def publish(
        self, topic: str, payload: str | None = None, retained: bool = False
    ):
        """
         Publish a message to the specified MQTT topic.
        :param topic: The MQTT topic to publish the message to.
        :param payload: The message payload.
        :param retained: Whether the message should be retained.
        """
        message = {
            "topic": topic,
            "retained": retained,
            "payload": payload,
        }
        async with self.session.post(
            "/mqtt/messages",
            json=message,
            headers=self.get_headers(),
        ) as response:
            result = await self.get_result(response)
            return result

    async def delete(self, topic: str):
        """
        Delete a message from the specified MQTT topic.
        :param topic: The MQTT topic to delete the message from.
        """
        async with self.session.delete(
            f"/mqtt/messages/{urllib.parse.quote_plus(topic)}",
            headers=self.get_headers(),
        ) as response:
            result = await self.get_result(response)
            return result
