from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Awaitable, List

    # from typehint.gateway import ReadyEvent

    from .client import WSClient
from logging import getLogger

logger = getLogger("reparty")
from discord_typings import ReadyEvent, GuildCreateData, GuildMemberAddData
class EventHandler:
    def __init__(self, ws: WSClient):
        self._ws = ws

    def __getitem__(self, __key) -> List[Awaitable]:
        return [
            getattr(self, "parse_" + __key.lower(), self.parse_unknown_event),
            # custom event
            getattr(self, "custom_parse_" + __key.lower(), self.parse_unknown_event),
        ]

    async def parse_unknown_event(self, data):
        pass

    async def parse_ready(self, data: ReadyEvent):
        self._ws._resume_gateway_url = data["resume_gateway_url"]
        self._ws._session_id = data["session_id"]

    async def parse_guild_create(self, data: GuildCreateData):
        logger.debug(f"Caching guild {data['id']}")
        self._ws.bot.cacher.add_guild_to_cache(data)

    async def parse_guild_member_add(self, data: GuildMemberAddData) -> None:
        logger.debug(f"Caching member {data['id']} of guild {data['guild_id']} to cache")
        self._ws.bot.cacher.add_member_to_cache(data)
