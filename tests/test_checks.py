"""Unittest for the command checks."""

import asyncio

from mrfreeze import checks

import pytest

from tests import helpers


@pytest.fixture()
def ctx():
    """Create a mock context object."""
    bot = helpers.MockMrFreeze()
    ctx = helpers.MockContext()
    ctx.bot = bot
    yield ctx


@pytest.fixture()
def loop():
    """Create a loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def test_is_owner_with_bot_is_owner_set_to_true(ctx, loop):
    """
    Test is_owner() with bot.is_owner() set to True.

    checks.is_owner() should always return the same result
    as bot.is_owner(), in this case True.
    """
    ctx.bot.is_owner.return_value = True
    result = loop.run_until_complete(checks.is_owner(ctx))

    assert result, "is_owner() should return True for owner"


def test_is_owner_with_bot_is_owner_set_to_false(ctx, loop):
    """
    Test is_owner() with bot.is_owner() set to False.

    checks.is_owner() should always return the same result
    as bot.is_owner(), in this case False.
    """
    ctx.bot.is_owner.return_value = False
    result = loop.run_until_complete(checks.is_owner(ctx))

    assert not result, "is_owner() should return False for non-owner"


def test_is_mod_with_ctx_object_and_authorised_caller(ctx, loop):
    """
    Test is_mod() with context object when caller is admin.

    Should return guild_permissions.administrator (== True).
    """
    ctx.author.guild_permissions.administrator = True
    result = loop.run_until_complete(checks.is_mod(ctx))

    assert result, "is_mod() should return True for admin"


def test_is_mod_with_ctx_object_and_unauthorised_caller(ctx, loop):
    """
    Test is_mod() with context object when caller is NOT admin.

    Should return guild_permissions.administrator (== False).
    """
    ctx.author.guild_permissions.administrator = False
    result = loop.run_until_complete(checks.is_mod(ctx))

    ctx.send.assert_called_with(
        "@member Only mods are allowed to use that command.")

    assert not result, "is_mod() should return False for non-admin"


def test_is_mod_with_ctx_object_and_unauthorised_caller_in_dm(ctx, loop):
    """
    Test is_mod() with context object when caller is NOT admin.

    Should return guild_permissions.administrator (== False).
    """
    ctx.guild = None
    result = loop.run_until_complete(checks.is_mod(ctx))

    ctx.send.assert_called_with(
        "Don't you try to sneak into my DMs and mod me!")

    assert not result, "is_mod() should return False for in DMs"


def test_is_mod_with_member_object_and_authorised_caller(ctx, loop):
    """
    Test is_mod() with member object when caller is admin.

    Should return guild_permissions.administrator (== True).
    """
    ctx.author.guild_permissions.administrator = True
    result = loop.run_until_complete(checks.is_mod(ctx.author))

    assert result, "is_mod() should return True for admin"


def test_is_mod_with_member_object_and_unauthorised_caller(ctx, loop):
    """
    Test is_mod() with member object when caller is NOT admin.

    Should return guild_permissions.administrator (== False).
    """
    ctx.author.guild_permissions.administrator = False
    result = loop.run_until_complete(checks.is_mod(ctx.author))

    assert not result, "is_mod() should return False for non-admin"


def test_always_allow_with_regular_user(ctx, loop):
    """
    Test always_allow() with non-owner non-admin member.

    Should return True.
    """
    ctx.bot.is_owner.return_value = False
    ctx.author.guild_permissions.administrator = False

    result = loop.run_until_complete(checks.always_allow(ctx.author))

    assert result, "always_allow() should return True for regular user"


def test_always_allow_with_non_owner_admin(ctx, loop):
    """
    Test always_allow() with non-owner admin member.

    Should return True.
    """
    ctx.bot.is_owner.return_value = False
    ctx.author.guild_permissions.administrator = True

    result = loop.run_until_complete(checks.always_allow(ctx.author))

    assert result, "always_allow() should return True for non-owner admin"


def test_always_allow_with_owner(ctx, loop):
    """
    Test always_allow() with owner non-admin member.

    Should return True.
    """
    ctx.bot.is_owner.return_value = True
    ctx.author.guild_permissions.administrator = False

    result = loop.run_until_complete(checks.always_allow(ctx.author))

    assert result, "always_allow() should return True for owner"


def test_always_deny_with_regular_user(ctx, loop):
    """
    Test always_deny() with non-owner non-admin member.

    Should return False.
    """
    ctx.bot.is_owner.return_value = False
    ctx.author.guild_permissions.administrator = False

    result = loop.run_until_complete(checks.always_deny(ctx.author))

    assert not result, "always_deny() should return False for regular user"


def test_always_deny_with_non_owner_admin(ctx, loop):
    """
    Test always_deny() with non-owner admin member.

    Should return False.
    """
    ctx.bot.is_owner.return_value = False
    ctx.author.guild_permissions.administrator = True

    result = loop.run_until_complete(checks.always_deny(ctx.author))

    assert not result, "always_deny() should return False for non-owner admin"


def test_always_deny_with_owner(ctx, loop):
    """
    Test always_deny() with owner non-admin member.

    Should return False.
    """
    ctx.bot.is_owner.return_value = True
    ctx.author.guild_permissions.administrator = False

    result = loop.run_until_complete(checks.always_deny(ctx.author))

    assert not result, "always_deny() should return False for owner"
