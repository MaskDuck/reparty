from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Awaitable, List

    # from typehint.gateway import ReadyEvent

    from .client import WSClient

from discord_typings import ReadyEvent
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
