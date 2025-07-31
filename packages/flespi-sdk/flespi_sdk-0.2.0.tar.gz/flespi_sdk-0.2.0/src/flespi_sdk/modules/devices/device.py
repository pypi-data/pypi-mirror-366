from aiohttp import ClientSession
from flespi_sdk.base.item import Item


class Device(Item):
    FIELDS = [
        "enabled",
        "device_type_id",
        "device_type_name",
        "protocol_id",
        "protocol_name",
        "configuration",
        "commands",
        "messages_size",
        "messages_ttl",
        "messages_rotate",
        "media_size",
        "media_ttl",
        "media_rotate",
        "media_traffic",
        "blocked",
        "media_blocked",
        "connected",
        "last_active",
        "telemetry",
        "settings",
        "commands_queue",
        "groups",
        "plugins",
        "streams",
        "calcs",
    ]

    def __init__(
        self,
        item: dict,
        session: ClientSession,
        operate_as: int,
    ):
        device_id = item["id"]
        super().__init__(
            id=device_id,
            item_path=f"/gw/devices/{device_id}",
            session=session,
            operate_as=operate_as,
        )

        self.enabled = None
        self.device_type_id = None
        self.device_type_name = None
        self.protocol_id = None
        self.protocol_name = None
        self.configuration = None
        self.commands = None
        self.messages_size = None
        self.messages_ttl = None
        self.messages_rotate = None
        self.media_size = None
        self.media_ttl = None
        self.media_rotate = None
        self.media_traffic = None
        self.blocked = None
        self.media_blocked = None
        self.connected = None
        self.last_active = None
        self.telemetry = None
        self.settings = None
        self.commands_queue = None
        self.groups = None
        self.plugins = None
        self.streams = None
        self.calcs = None
        self._update_fields(item=item)
