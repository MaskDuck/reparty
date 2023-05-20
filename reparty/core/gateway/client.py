from __future__ import annotations

from logging import getLogger
from sys import platform as _os
from typing import TYPE_CHECKING

from aiohttp import ClientSession, WSMsgType

if TYPE_CHECKING:
    from typing import Optional, List, Literal

    from aiohttp import ClientWebSocketResponse

    # from ...typehint.gateway import GatewayEvent, UpdatePresenceData
    from .event_handler import EventHandler

from discord_typings import (ActivityData, GatewayEvent, GuildMemberData,
                             Snowflake, UpdatePresenceData)

__all__ = "WSClient"

from asyncio import TimeoutError, create_task
from asyncio import run as run_async
from asyncio import sleep
from random import randint

from ...utils import zjson_from_msg
from ..errors.gateway import GatewayClosed
from .event_handler import EventHandler

logger = getLogger("reparty")


class Opcodes:
    # fmt: off
    dispatch              = 0
    heartbeat             = 1
    identify              = 2
    presence_update       = 3
    voice_state_update    = 4
    resume                = 6
    reconnect             = 7
    request_guild_members = 8
    invalid_session       = 9
    hello                 = 10
    heartbeat_ack         = 11
    # fmt: on


class WSClient:
    if TYPE_CHECKING:
        _ws: ClientWebSocketResponse
        _heartbeat_interval: int
        _resume_gateway_url: str
        _session_id: str

    def __init__(
        self,
        *,
        token: str,
        intents: int,
        bot,  # in exceptional circumstances, bot can be None
        activities: Optional[UpdatePresenceData] = None,
        dispatcher: Optional[EventHandler] = None,
        session: Optional[ClientSession] = None,  # for existing session
    ):
        self._token: str = token
        self._session: Optional[ClientSession] = session
        self._api_version: int = 10
        self._gw_url: str = f"wss://gateway.discord.gg/?v={self._api_version}&encoding=json&compress=zlib-stream"
        self._intents: int = intents
        self._last_sequence: Optional[int] = None
        self._activities_payload = activities
        self._dispatcher = dispatcher if dispatcher else EventHandler(self)
        self._heartbeat_fail: int = 0
        self._resuming_gateway_url: Optional[str] = None
        self.bot = bot

    async def change_presence(
        self,
        since: Optional[int] = None,
        activities: Optional[List[ActivityData]] = None,
        status: Literal["dnd", "streaming", "online", "idle", "invisible"] = None,
        afk: Optional[bool] = None,
    ):
        payload = {}
        if since:
            payload["since"] = since
        if activities:
            payload["activities"] = activities
        if status:
            payload["status"] = status
        if afk:
            payload["afk"] = afk

        await self._ws.send_json(payload)

    async def request_guild_members(
        self,
        *,
        guild_id: Snowflake,
        query: str = "",
        limit: int = 0,
        presences: bool = False,
        user_ids: List[Snowflake] = [],
        nonce: Optional[str] = None,
    ) -> None:
        payload = {
            "guild_id": str(guild_id),
            "query": query,
            "limit": limit,
            "presences": presences,
            "user_ids": user_ids,
        }
        if nonce:
            payload["nonce"] = nonce

        await self._ws.send_json(payload)

    @property
    def resume_payload(self):
        return {
            "op": Opcodes.resume,
            "d": {
                "token": self._token,
                "seq": self._last_sequence,
                "session_id": self._session_id,
            },
        }

    async def _ping(self) -> None:
        await self._ws.send_json({"op": Opcodes.heartbeat, "d": self._last_sequence})

    async def _keep_connection(self) -> None:
        while True:
            await self._ping()
            await sleep(self._heartbeat_interval / 1000)

    @property
    def identify_payload(self) -> None:
        o = {
            "op": Opcodes.identify,
            "d": {
                "token": self._token,
                "intents": self._intents,
                "properties": {"os": _os, "browser": "reparty", "device": "reparty"},
                "compress": True,
            },
        }
        if a := self._activities_payload:
            o["presence"] = a
        return o

    async def _connect(self, resuming: bool = False) -> None:
        gw_url = self._resume_gateway_url if resuming else self._gw_url
        if self._session is None:
            self._session = ClientSession()
        async with self._session.ws_connect(gw_url) as ws:
            self._ws = ws
            async for msg in self._ws:
                logger.debug(f"New data from WS")
                payload: GatewayEvent = zjson_from_msg(msg)
                logger.debug(payload)
                self._last_sequence = payload["s"]
                if payload["op"] == Opcodes.hello:
                    self._heartbeat_interval = payload["d"]["heartbeat_interval"]
                    create_task(self._keep_connection())

                    if resuming:
                        await self._ws.send_json(self.resume_payload)
                    else:
                        await self._ws.send_json(self.identify_payload)
                    jitter = randint(0, 1)
                    await sleep(float(jitter))
                elif payload["op"] == Opcodes.heartbeat:
                    await self._ping()
                elif payload["op"] == Opcodes.dispatch:
                    # print(f"Event {payload['t']}")
                    logger.debug(f"Event {payload['t']}")
                    for x in self._dispatcher[payload["t"]]:  # type: ignore
                        await x(payload["d"])  # type: ignore
                elif payload["op"] == Opcodes.reconnect:
                    await self._ws.close(code=4001)
                    await self._connect(resuming=True)
                elif payload["op"] == Opcodes.invalid_session:
                    await self._ws.close(code=4001)
                    if payload["d"]:
                        await self._connect(resuming=True)
                    else:
                        await self._connect()

                    # TODO: probably handle these in order to prevent improperly informed disconnections
                elif msg.type == WSMsgType.CLOSE:
                    raise GatewayClosed(msg.data, msg.extra)

    def connect(self, resuming=False) -> None:
        try:
            run_async(self._connect(resuming=resuming))
        except KeyboardInterrupt:
            run_async(self._session.close())
