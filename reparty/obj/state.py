from __future__ import annotations

from typing import Dict, List

from discord_typings import (
        GuildCreateData,
        GuildData, 
        GuildMemberAddData,                     
        GuildMemberData, 
        Snowflake,
        ChannelUpdateData, 
        ChannelData,
)


class Cacher:
    def __init__(self, bot):
        self._bot = bot
        self._all_guilds: Dict[str, GuildData] = {}
        self._guild_members: Dict[str, List[GuildMemberData]] = {}
        # the dict self._guild_members consists of 2 things: the key is the snowflake of the guild
        # the value is the guild member
        self._channels: Dict[Snowflake, List[ChannelData]] = {}

    def add_channel_to_cache(self, channel: ChannelData):
        self._channels[channel['id']] = channel

    def fetch_channel_from_cache(self, channel_id: Snowflake) -> None | ChannelData:
        return self._channels.get(str(channel_id))

    def remove_channel_from_cache(self, channel_id: Snowflake) -> None:
        self._channels.pop(str(channel_id))

    def edit_channel_from_cache(self, channel: ChannelUpdateData):
        self._channels[channel['id']] = channel

    def add_guild_to_cache(self, guild: GuildCreateData):
        self._all_guilds[guild["id"]] = guild
        self._create_empty_guild_member_slot(guild["id"])

    def fetch_guild_from_cache(self, id: Snowflake) -> GuildData:
        return self._all_guilds[str(id)]

    def add_member_to_cache(self, member: GuildMemberAddData):
        assert member.get("guild_id") is not None, "guild_id not found"
        guild_id = member.pop("guild_id")  # type: ignore
        self._guild_members[guild_id].append(member)  # type: ignore
        # this has become GuildMemberData

    def get_member_from_cache(self, guild_id: str, member_id: str) -> GuildMemberData:
        # assert x.get("user") is not None, "no user found"
        return [
            x for x in self._guild_members[guild_id] if x["user"]["id"] == member_id
        ][0]

    def _create_empty_guild_member_slot(self, guild_id: str) -> None:
        self._guild_members[guild_id] = []
