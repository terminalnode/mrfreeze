"""
Various useful mock objects and helper objects for testing the bot.

Most of this code derives from the Python discord server's bot,
the original code can be found here:
https://github.com/python-discord/bot/blob/master/tests/helpers.py
"""

import collections
import inspect
import itertools
from typing import Any, Iterable, Optional
from unittest.mock import AsyncMock, MagicMock

import discord
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze

guild_data = {
    "id": 1,
    "name": "guild",
    "region": "Europe",
    "verification_level": 2,
    "default_notications": 1,
    "afk_timeout": 100,
    "icon": "icon.png",
    "banner": "banner.png",
    "mfa_level": 1,
    "splash": "splash.png",
    "system_channel_id": 464033278631084042,
    "description": "mocking is painful",
    "max_presences": 10_000,
    "max_members": 100_000,
    "preferred_locale": "UTC",
    "owner_id": 1,
    "afk_channel_id": 464033278631084042}

guild_instance = discord.Guild(
    data=guild_data,
    state=MagicMock())

member_data = {"user": "lemon", "roles": [1]}
state_mock = MagicMock()
member_instance = discord.Member(
    data=member_data,
    guild=guild_instance,
    state=state_mock)

role_data = {"name": "role", "id": 1}
role_instance = discord.Role(
    guild=guild_instance,
    state=MagicMock(),
    data=role_data)

context_instance = Context(message=MagicMock(), prefix=MagicMock())

message_data = {
    "id": 1,
    "webhook_id": 431341013479718912,
    "attachments": [],
    "embeds": [],
    "application": "Python Discord",
    "activity": "mocking",
    "channel": MagicMock(),
    "edited_timestamp": "2019-10-14T15:33:48+00:00",
    "type": "message",
    "pinned": False,
    "mention_everyone": False,
    "tts": None,
    "content": "content",
    "nonce": None}

channel_data = {
    "id": 1,
    "type": "TextChannel",
    "name": "channel",
    "parent_id": 1234567890,
    "topic": "topic",
    "position": 1,
    "nsfw": False,
    "last_message_id": 1,
}

state = MagicMock()
channel = MagicMock()
guild = MagicMock()

message_instance = discord.Message(
    state=state,
    channel=channel,
    data=message_data)

channel_instance = discord.TextChannel(
    state=state,
    guild=guild,
    data=channel_data)

# TODO: Add some option to MrFreeze for skipping
#       the directory configuration thing.
bot_instance = MrFreeze(command_prefix=MagicMock())
bot_instance.http_session = None
bot_instance.api_client = None


class CustomMockMixin(MagicMock):
    child_mock_type = MagicMock
    discord_id = itertools.count(0)

    def __init__(self, spec_set: Any = None, **kw):
        name = kw.pop("name", None)
        super().__init__(
                spec_set=spec_set,
                **kw)

        if name:
            self.name = name
        if spec_set:
            self._get_coroutines_from_spec_instance(spec_set)

    def _get_child_mock(self, **kw):
        klass = self.child_mock_type

        if self._mock_sealed:
            attribute = "." + kw["name"] if "name" in kw else "()"
            mock_name = self._extract_mock_name() + attribute
            raise AttributeError(mock_name)

        return klass(**kw)

    def _get_coroutines_from_spec_instance(self, source: Any) -> None:
        for name, _method in inspect.getmembers(
                source,
                inspect.iscoroutinefunction):
            setattr(self, name, AsyncMock())


class HashableMixin(discord.mixins.EqualityComparable):
    def __hash__(self):
        return self.id


class ColourMixin():
    @property
    def color(self) -> discord.Colour:
        return self.colour

    @color.setter
    def color(self, color: discord.Colour) -> None:
        self.colour = color


class MockRole(CustomMockMixin, AsyncMock, HashableMixin):
    """Mock of discord.Role."""

    def __init__(self, **kwargs) -> None:
        default_kwargs = {
            "id": next(self.discord_id),
            "name":
            "role",
            "position": 1}

        super().__init__(
            spec_set=role_instance,
            **collections.ChainMap(kwargs, default_kwargs))

        if "mention" not in kwargs:
            self.mention = f"&{self.name}"

    def __lt__(self, other):
        return self.position < other.position


class MockGuild(CustomMockMixin, AsyncMock, HashableMixin):
    """Mock of discord.Guild."""

    def __init__(self,
                 roles: Optional[Iterable[MockRole]] = None,
                 **kwargs) -> None:
        default_kwargs = {
            "id": next(self.discord_id),
            "members": []}

        super().__init__(
            spec_set=guild_instance,
            **collections.ChainMap(
                kwargs,
                default_kwargs))

        self.roles = [MockRole(name="@everyone", position=1, id=0)]
        if roles:
            self.roles.extend(roles)


class MockMember(CustomMockMixin, AsyncMock, ColourMixin, HashableMixin):
    """Mock of discord.Member."""

    def __init__(self,
                 roles: Optional[Iterable[MockRole]] = None,
                 **kwargs) -> None:
        default_kwargs = {
            "name": "member",
            "id": next(self.discord_id)}

        super().__init__(
            spec_set=member_instance,
            **collections.ChainMap(kwargs, default_kwargs))

        self.roles = [MockRole(name="@everyone", position=1, id=0)]
        if roles:
            self.roles.extend(roles)

        if "mention" not in kwargs:
            self.mention = f"@{self.name}"


class MockMrFreeze(CustomMockMixin, AsyncMock):
    """Mock of mrfreeze.MrFreeze."""

    def __init__(self, **kwargs) -> None:
        super().__init__(spec_set=bot_instance, **kwargs)

        # self.wait_for is *not* a coroutine function, but returns a
        # coroutine nonetheless and and should therefore be awaited.
        # (The documentation calls it a coroutine as well, which
        # is technically incorrect, since it's a regular def.)
        self.wait_for = AsyncMock()

        # Since calling `create_task` on our MockBot does not actually
        # schedule the coroutine object as a task in the asyncio loop,
        # this `side_effect` calls `close()` on the coroutine object
        # to prevent "has not been awaited"-warnings.
        self.loop.create_task.side_effect = lambda coroutine: coroutine.close()


class MockTextChannel(CustomMockMixin, AsyncMock, HashableMixin):
    """Mock of discord.TextChannel."""

    def __init__(self,
                 name: str = "channel",
                 channel_id: int = 1,
                 **kwargs) -> None:
        default_kwargs = {
            "id": next(self.discord_id),
            "name": "channel",
            "guild": MockGuild()}
        super().__init__(
            spec_set=channel_instance,
            **collections.ChainMap(kwargs, default_kwargs))

        if "mention" not in kwargs:
            self.mention = f"#{self.name}"


class MockContext(CustomMockMixin, AsyncMock):
    """Mock of discord.ext.commands.Context."""

    def __init__(self, **kwargs) -> None:
        super().__init__(
            spec_set=context_instance,
            **kwargs)
        self.bot = kwargs.get("bot", MockMrFreeze())
        self.guild = kwargs.get("guild", MockGuild())
        self.author = kwargs.get("author", MockMember())
        self.channel = kwargs.get("channel", MockTextChannel())


class MockMessage(CustomMockMixin, AsyncMock):
    """Mock of discord.Message."""

    def __init__(self, **kwargs) -> None:
        super().__init__(
            spec_set=message_instance,
            **kwargs)
        self.author = kwargs.get("author", MockMember())
        self.channel = kwargs.get("channel", MockTextChannel())
