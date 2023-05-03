from __future__ import annotations

from typing import Dict, List

from discord_typings import (GuildCreateData, GuildData, GuildMemberAddData,
                             GuildMemberData, Snowflake)


class Cacher:
    def __init__(self, bot):
        self._bot = bot
        self._all_guilds: Dict[Snowflake, GuildData] = {}
        self._guild_members: Dict[Snowflake, List[GuildMemberData]] = {}
        # the dict self._guild_members consists of 2 things: the key is the snowflake of the guild
        # the value is the guild member

    def add_guild_to_cache(self, guild: GuildCreateData):
        self._all_guilds[guild["id"]] = guild

    def fetch_guild_from_cache(self, id: Snowflake) -> GuildData:
        return self._all_guilds[id]

    def add_member_to_cache(self, member: GuildMemberAddData):
        guild_id = member.pop("guild_id")
        self._guild_members[guild_id].append(member)

    def get_member_from_cache(self, guild_id: str, member_id: str) -> GuildMemberData:
        return [x for x in self._guild_members[guild_id] if x['user']['id'] == member_id][0]

    def create_empty_guild_member_slot(self, guild_id: str) -> None:
        self._guild_members[guild_id] = []
