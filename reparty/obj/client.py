from __future__ import annotations

from traceback import format_exception, print_exception
from typing import (Any, AnyStr, Awaitable, Generic, List, Optional, TypeVar,
                    Union)

from discord_typings import Snowflake as SnowflakeType, ChannelData
from reparty.core.gateway.client import WSClient
from reparty.core.http.request import RequestInformation, Requestor
from reparty.obj.message import Message
from reparty.obj.snowflake import Snowflake
from reparty.obj.state import Cacher
from reparty.typehint import Empty

# TODO: cache
# HR = TypeVar(name="HR", bound="HasRepr")  # type: ignore
S = TypeVar(name="S", bound="Union[str, int]")  # type: ignore


class Client:
    """Client object.
    You should fetch the object if you want a type-safe interface.
    Most functions described on this is NOT type-safe. Use at your own risk.
    """

    def __init__(
        self,
        *,
        token: str,
        intents: int,  # TODO: it is needed to turn this into flags
    ) -> None:
        self._token = token
        self.intents = intents
        self._ws_client = WSClient(token=token, intents=intents, bot=self)
        self._http_client = Requestor(token=token)
        self._custom_event_handlers: dict[str, Awaitable] = {}
        # self._ws_client.bot = self
        self.cacher: Cacher = Cacher(self)

    def listener(self, func: Awaitable):
        def inner(name=func.__name__):  # type: ignore
            self._custom_event_handlers[name] = func

        return inner

    async def send_message(
        self,
        channel_id: S,  # type: ignore
        # content: AnyStr = Empty,
        **kwargs,
        # nonce: Union[str, int] = Empty,
        # tts: bool = Empty,
        # embed: ... = Empty,  # TODO: Embed typehint
        # embeds: List[...] = [],  # TODO: Embed typehint
        # allowed_mentions: ... = Empty,  # TODO: Allowed mentions typehint
        # message_references: ... = Empty,  # TODO: Message reference typehint
        # components: List[...] = Empty,  # TODO: Component typehint
        # sticker_ids: List[int] = Empty,
        # files: List[...] = Empty,  # TODO: this is gonna needs a lot of works
        # # I don't think I'll be able to do the work myself...
        # payload_json: List[dict[str, Any]] = Empty,  # TODO: same as above
        # attachments: List[...] = Empty,  # TODO: same as above, Attachment typehint
        # flags: Union[int, ...] = Empty,  # TODO: Flag object
    ) -> Optional[Message]:
        # p = {}
        # if content is not Empty:
        #    p["content"] = str(content)
        # if nonce is not Empty:
        #    p["nonce"] = nonce
        # if tts is not Empty:
        #    p["tts"] = tts
        # if embed is not Empty:
        #    embeds.append(embed)
        # if embeds is not []:
        #    p["embeds"] = [x.payload for x in embeds]
        # if allowed_mentions is not Empty:
        #    p["allowed_mentions"] = allowed_mentions.payload
        # if message_references is not Empty:
        #    p["message_references"] = message_references.payload
        # if components is not Empty:
        #    p["components"] = [x.payload for x in components]
        # if sticker_ids is not Empty:
        #    p["sticker_ids"] = sticker_ids
        ## TODO: implement files
        r = RequestInformation(
            method="POST",
            route=f"/channels/{channel_id}/messages",
            json=kwargs,
        )
        y = await self._http_client.request(r)
        if y.ok:
            return Message(data=y.json, bot=self)  # type: ignore

        # print(y)

    async def delete_message(
        self, channel_id: SnowflakeType, message_id: SnowflakeType
    ):
        r = RequestInformation(
            method="DELETE", route=f"/channels/{channel_id}/messages/{message_id}"
        )
        await self._http_client.request(r)

    async def bulk_delete_message(
        self, channel_id: SnowflakeType, messages_id: list[SnowflakeType]
    ) -> None:
        assert 2 <= len(messages_id) <= 100, "Too many messages"
        messages_id = [str(x) for x in messages_id]
        r = RequestInformation(
            method="POST",
            route=f"/channels/{channel_id}/messages/bulk_delete",
            json={"messages": messages_id},
        )
        await self._http_client.request(r)

    async def crosspost_message(
        self, channel_id: SnowflakeType, message_id: SnowflakeType
    ) -> None:
        r = RequestInformation(
            method="POST",
            route=f"/channels/{channel_id}/messages/{message_id}/crosspost",
        )
        await self._http_client.request(r)

    async def edit_message(
        self,
        channel_id: SnowflakeType,
        message_id: SnowflakeType,
        **kwargs,
    ) -> Optional[Message]:
        r = RequestInformation(
            route=f"/channels/{channel_id}/messages/{message_id}",
            method="PATCH",
            json=kwargs,
        )
        x = await self._http_client.request(r)
        if x.ok:
            return Message(bot=self, data=x.json)

    async def pin_message(self,
                  channel_id: SnowflakeType,
                  message_id: SnowflakeType,
                ) -> None:
        r = RequestInformation(
                route=f"/channels/{channel_id}/pins/{message_id}",
                method="PUT",
        )
        await self._http_client.request(r)

    async def start_thread_from_message(
            self,
            channel_id: SnowflakeType,
            message_id: SnowflakeType,
            reason: Optional[str] = None,
            **kwargs,
            ) -> Optional[ChannelData]:  # TODO: Channel Object typehint
        r = RequestInformation(
                route=f"/channels/{channel_id}/messages/{message_id}/threads",
                method="POST",
                json=kwargs
            )
        x = await self._http_client.request(r)
        if x.ok:
            return x.json
        


    # def send_message(
    #    self,
    #   content: Any
    # )

    # async def change_presence(self, )

    def start(self):
        self._ws_client.connect()
