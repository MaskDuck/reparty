from __future__ import annotations
from typing import TYPE_CHECKING
from aiohttp import ClientSession, WSMsgType

from sys import platform as _os

if TYPE_CHECKING:
    from typing import Optional
    from aiohttp import ClientWebSocketResponse

    from ...typehint.gateway import UpdatePresenceData, GatewayEvent
    from .event_handler import EventHandler

try:
    from orjson import loads, dumps
except ImportError:
    from json import (  # noqa: F401 -- this is used in case we can't import orjson
        loads,
        dumps,
    )  


from utils import zjson_from_msg
from asyncio import sleep, ensure_future, TimeoutError

from random import randint
from ..errors.gateway import GatewayClosed


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
        activities: Optional[UpdatePresenceData] = None,
        dispatcher: EventHandler = None,
    ):
        self._token: str = token
        self._session: Optional[ClientSession] = None
        self._api_version: int = 10
        self._gw_url: str = f"wss://gateway.discord.gg/?v={self._api_version}&encoding=json&compress=zlib-stream"
        self._intents: int = intents
        self._last_sequence: Optional[int] = None
        self._activities_payload = activities
        self._dispatcher = dispatcher if dispatcher else EventHandler(self)
        self._heartbeat_fail: int = 0

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
        if TYPE_CHECKING:
            self._ws: ClientWebSocketResponse

        await self._ws.send_json({"op": Opcodes.heartbeat, "d": self._last_sequence})
        try:
            r = await self._ws.receive(timeout=2.0)
            r = await zjson_from_msg(r)
            if r["op"] == Opcodes.heartbeat_ack:
                self._heartbeat_fail = 0
            else:
                self._heartbeat_fail += 1
                if self._heartbeat_fail >= 5:
                    await self._ws.close(code=4001)
        except TimeoutError:
            self._heartbeat_fail += 1
            if self._heartbeat_fail >= 5:
                await self._ws.close(code=4001)

    async def _keep_connection(self) -> None:
        while True:
            await self._ping()
            await sleep(self._heartbeat_interval)

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

    async def connect(self, resuming: bool = False) -> None:
        gw_url = self._resume_gateway_url if resuming else self._gw_url
        if self._session is None:
            self._session = ClientSession()
        async with self._session.ws_connect(gw_url) as ws:
            self._ws = ws
            async for msg in self._ws:
                payload: GatewayEvent = zjson_from_msg(msg)
                self._last_sequence = payload["s"]
                if payload["op"] == Opcodes.hello:
                    self._heartbeat_interval = payload["d"]["heartbeat_interval"]

                    jitter = randint(0, 1)
                    await sleep(float(jitter))
                    await ensure_future(self._keep_connection())
                    if resuming:
                        await self._ws.send_json(self.resume_payload)
                    else:
                        await self._ws.send_json({}, dumps=dumps)
                elif payload["op"] == Opcodes.heartbeat:
                    await self._ping()
                elif payload["op"] == Opcodes.dispatch:
                    await self._dispatcher[payload["t"]](payload["d"])
                elif payload["op"] == Opcodes.reconnect:
                    await self._ws.close(code=4001)
                    await self.connect(resuming=True)
                elif payload["op"] == Opcodes.invalid_session:
                    await self._ws.close(code=4001)
                    await self.connect()
                elif msg.type == WSMsgType.CLOSE:
                    raise GatewayClosed(msg.data, msg.extra)
