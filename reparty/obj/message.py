from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Union, Literal

from reparty.core.http.request import RequestInformation
from reparty.obj.snowflake import Snowflake


if TYPE_CHECKING:
    from discord_typings import (ActivityData, AttachmentData,
                                 ChannelMentionData, ComponentData, EmbedData,
                                 GuildMemberData, MessageActivityData,
                                 MessageData, MessageInteractionData,
                                 MessageReactionData, MessageReferenceData,
                                 MessageTypes, PartialApplicationData)
    from discord_typings import Snowflake as SnowflakeType
    from discord_typings import (StickerItemData, ThreadChannelData, UserData,
                                 UserMentionData)
    from discord_typings import ChannelData

    from .client import Client
    from ..typehint import Empty, Undefined 


class Message(Snowflake):
    def __init__(self, *, data: MessageData, bot: Client):
        self._bot: Client = bot
        self.id: int = int(data["id"])
        self.channel_id: int = int(data["channel_id"])
        self.channel: SnowflakeType = data[
            "channel_id"
        ]  # TODO: Channel object replacement
        self.author: Union[UserData, GuildMemberData] = data[
            "author"
        ]  # TODO: User/Member object replacement

        self.content: str = data["content"]  # without msg content it is ""
        self.timestamp: datetime = datetime.fromisoformat(data["timestamp"])
        if x := data["edited_timestamp"]:
            self.edited_timestamp: Optional[datetime] = datetime.fromisoformat(x)
        else:
            self.edited_timestamp: Optional[datetime] = None
        self.tts: bool = data["tts"]
        self.mention_everyone: bool = data["mention_everyone"]
        self.mentions: Union[list[UserMentionData], list[UserData]] = data[
            "mentions"
        ]  # TODO: User object
        self.mention_roles: list[SnowflakeType] = data["mention_roles"]

        self.attachments: list[AttachmentData] = data[
            "attachments"
        ]  # TODO: Attachment object
        self.embeds: list[EmbedData] = data["embeds"]  # TODO: Embed object
        self.pinned: bool = data["pinned"]
        self.type: MessageTypes = data["type"]  # TODO: Message type enum
        if mention_channels := data.get("mention_channels"):
            self.mention_channels: list[
                ChannelMentionData
            ] = mention_channels  # TODO: Channel mention obj
        else:
            self.mention_channels: list[ChannelMentionData] = []

        if reactions := data.get("reactions"):
            self.reactions: list[
                MessageReactionData
            ] = reactions  # TODO: Reaction object
        else:
            self.reactions: list[MessageReactionData] = []

        if nonce := data.get("nonce"):
            self.nonce: Optional[Union[str, int]] = nonce
        else:
            self.nonce: Optional[Union[str, int]] = None
        if webhook_id := data.get("webhook_id"):
            self.webhook_id: Optional[int] = int(webhook_id)
        else:
            self.webhook_id: Optional[int] = None

        if activity := data.get("activity"):
            self.activity: Optional[
                MessageActivityData
            ] = activity  # TODO: Message Activity object
        else:
            self.activity: Optional[MessageActivityData] = None

        if application := data.get("application"):
            self.application: Optional[
                PartialApplicationData
            ] = application  # type: ignore  # TODO: Partial Application object
        else:
            self.application: Optional[PartialApplicationData] = None

        if application_id := data.get("application_id"):
            self.application_id: Optional[int] = int(application_id)
        else:
            self.application_id: Optional[int] = None

        if message_reference := data.get("message_reference"):
            self.message_reference: Optional[
                MessageReferenceData
            ] = message_reference  # TODO: msg ref object
        else:
            self.message_reference: Optional[MessageReferenceData] = None

        if flags := data.get("flags"):
            self.flags: Optional[int] = flags  # TODO: msg flags
        else:
            self.flags: Optional[int] = flags

        if referenced_message := data.get("referenced_message"):
            self.referenced_message: Optional[Message] = referenced_message
        else:
            self.referenced_message: Optional[Message] = None

        if interaction := data.get("interaction"):
            self.interaction: Optional[
                MessageInteractionData
            ] = interaction  # TODO: Message Interaction object
        else:
            self.interaction: Optional[MessageInteractionData] = None

        if thread := data.get("thread"):
            self.thread: Optional[ThreadChannelData] = thread  # TODO: Thread object
        else:
            self.thread: Optional[ThreadChannelData] = None

        if components := data.get("components"):
            self.components: Optional[
                list[ComponentData]
            ] = components  # TODO: Component Object
        else:
            self.components: Optional[list[ComponentData]] = components

        if sticker_items := data.get("sticker_items"):
            self.sticker_items: Optional[
                list[StickerItemData]
            ] = sticker_items  # TODO: Sticker object
        else:
            self.sticker_items: Optional[list[StickerItemData]] = None

        if position := data.get("position"):
            self.position: Optional[int] = position
        else:
            self.position: Optional[int] = position

        # TODO: Role subscription data, discord_typings needs these first

    async def crosspost(self):
        await self._bot.crosspost_message(self.channel_id, self.id)

    async def delete(self):
        await self._bot.delete_message(self.channel_id, self.id)

    async def pin(self):
        await self._bot.pin_message(self.channel_id, self.id)

    async def start_thread(
            self,
            *,
            name: str,
            auto_archive_duration: Optional[Literal[60, 1440, 4320, 10080]] | Undefined =Empty,
            rate_limit_per_user: Optional[int] | Undefined = Empty
        ) -> Optional[ChannelData]:
        return await self._bot.start_thread_from_message(
                self.channel_id,
                self.id,
                auto_archive_duration=auto_archive_duration,
                rate_limit_per_user=rate_limit_per_user
            )

    
         

