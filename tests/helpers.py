# This code derives a lot from the Python discord's bot:
# https://github.com/python-discord/bot/blob/master/tests/helpers.py
# And by derives I mean that it's basically copy-paste with small changes.

import collections
import itertools
import inspect
import unittest.mock
from typing import Any
from typing import Iterable
from typing import Optional

import discord

from mrfreeze.bot import MrFreeze

guild_data = {
    'id': 1,
    'name': 'guild',
    'region': 'Europe',
    'verification_level': 2,
    'default_notications': 1,
    'afk_timeout': 100,
    'icon': "icon.png",
    'banner': 'banner.png',
    'mfa_level': 1,
    'splash': 'splash.png',
    'system_channel_id': 464033278631084042,
    'description': 'mocking is fun',
    'max_presences': 10_000,
    'max_members': 100_000,
    'preferred_locale': 'UTC',
    'owner_id': 1,
    'afk_channel_id': 464033278631084042,
}

guild_instance = discord.Guild(
    data=guild_data,
    state=unittest.mock.MagicMock()
)

member_data = {'user': 'lemon', 'roles': [1]}
state_mock = unittest.mock.MagicMock()
member_instance = discord.Member(
    data=member_data,
    guild=guild_instance,
    state=state_mock)

role_data = {'name': 'role', 'id': 1}
role_instance = discord.Role(
    guild=guild_instance,
    state=unittest.mock.MagicMock(),
    data=role_data
)

bot_instance = MrFreeze(command_prefix=unittest.mock.MagicMock())
bot_instance.http_session = None
bot_instance.api_client = None

class CustomMockMixin(unittest.mock.MagicMock):
    child_mock_type = unittest.mock.MagicMock
    discord_id = itertools.count(0)

    def __init__(self, spec_set: Any = None, **kwargs):
        name = kwargs.pop('name', None)
        super().__init__(spec_set=spec_set, **kwargs)

        if name:
            self.name = name
        if spec_set:
            self._extract_coroutine_methods_from_spec_instance(spec_set)

    def _get_child_mock(self, **kw):
        klass = self.child_mock_type

        if self._mock_sealed:
            attribute = "." + kw["name"] if "name" in kw else "()"
            mock_name = self._extract_mock_name() + attribute
            raise AttributeError(mock_name)

        return klass(**kw)

    def _extract_coroutine_methods_from_spec_instance(self, source: Any) -> None:
        for name, _method in inspect.getmembers(
                source,
                inspect.iscoroutinefunction):
            setattr(self, name, unittest.mock.AsyncMock())


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


class MockRole(CustomMockMixin, unittest.mock.AsyncMock, HashableMixin):
    def __init__(self, **kwargs) -> None:
        default_kwargs = {
            "id": next(self.discord_id),
            "name":
            "role",
            "position": 1
        }

        super().__init__(
            spec_set=role_instance,
            **collections.ChainMap(kwargs, default_kwargs)
        )

        if "mention" not in kwargs:
            self.mention = f"&{self.name}"

    def __lt__(self, other):
        """
        Simplified position-based comparisons
        similar to those of `discord.Role`.
        """
        return self.position < other.position


class MockGuild(CustomMockMixin, unittest.mock.AsyncMock, HashableMixin):
    def __init__(self, roles: Optional[Iterable[MockRole]] = None, **kwargs) -> None:
        default_kwargs = {
            "id": next(self.discord_id),
            "members": []
        }
        super().__init__(
            spec_set=guild_instance,
            **collections.ChainMap(
                kwargs,
                default_kwargs)
            )

        self.roles = [MockRole(name="@everyone", position=1, id=0)]
        if roles:
            self.roles.extend(roles)


class MockMember(CustomMockMixin, unittest.mock.AsyncMock, ColourMixin, HashableMixin):
    def __init__(self, roles: Optional[Iterable[MockRole]] = None, **kwargs) -> None:
        default_kwargs = {'name': 'member', 'id': next(self.discord_id)}
        super().__init__(
            spec_set=member_instance,
            **collections.ChainMap(kwargs, default_kwargs)
        )

        self.roles = [MockRole(name="@everyone", position=1, id=0)]
        if roles:
            self.roles.extend(roles)

        if 'mention' not in kwargs:
            self.mention = f"@{self.name}"


class MockMrFreeze(CustomMockMixin, unittest.mock.AsyncMock):
    def __init__(self, **kwargs) -> None:
        super().__init__(spec_set=bot_instance, **kwargs)

        # self.wait_for is *not* a coroutine function, but returns a
        # coroutine nonetheless and and should therefore be awaited.
        # (The documentation calls it a coroutine as well, which
        # is technically incorrect, since it's a regular def.)
        self.wait_for = unittest.mock.AsyncMock()

        # Since calling `create_task` on our MockBot does not actually
        # schedule the coroutine object as a task in the asyncio loop,
        # this `side_effect` calls `close()` on the coroutine object
        # to prevent "has not been awaited"-warnings.
        self.loop.create_task.side_effect = lambda coroutine: coroutine.close()
