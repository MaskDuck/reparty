from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Awaitable, List

    # from typehint.gateway import ReadyEvent

    from .client import WSClient
from logging import getLogger

logger = getLogger("reparty")
from discord_typings import ReadyData, GuildCreateData, GuildMemberAddData, ChannelCreateData
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

    async def parse_ready(self, data: ReadyData):
        self._ws._resume_gateway_url = data["resume_gateway_url"]  # type: ignore
        self._ws._session_id = data["session_id"]

    async def parse_guild_create(self, data: GuildCreateData):
        logger.debug(f"Caching guild {data['id']}")
        self._ws.bot.cacher.add_guild_to_cache(data)  # type: ignore
        # expected higher on TCs but they're dumb nowadays, cacher is guaranteed not to be None.
        # self._ws.bot.cacher.create_empty_guild_member_slot(data['id'])
        for x in data['members']:
            x['guild_id'] = data['id']  # type: ignore -- this is setting operation, not adding operation
            self._ws.bot.cacher.add_member_to_cache(x)

    async def parse_guild_member_add(self, data: GuildMemberAddData) -> None:
        logger.debug(f"Caching member {data['user']['id']} of guild {data['guild_id']} to cache")
        self._ws.bot.cacher.add_member_to_cache(data)

    async def parse_channel_create(self, data: ChannelCreateData):
        self._ws.bot.cacher.add_channel_to_cache(data)
    
    
