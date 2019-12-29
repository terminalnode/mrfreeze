"""Unittest for the command checks."""

import asyncio
import unittest

from mrfreeze import checks

from tests import helpers

# TODO
# is_mod() doesn't yet test the response messages of guild-less ctx calls

class ChecksUnitTest(unittest.TestCase):
    """Test the command checks."""

    def setUp(self):
        """
        Set up a clean environment for each test.

        Each check takes a context object, except for is_mod
        which can take either a context object or a member object.
        """
        self.ctx = helpers.MockContext()
        self.ctx.bot = helpers.MockMrFreeze()
        self.member = self.ctx.author
        self.loop = asyncio.new_event_loop()

    def tearDown(self):
        """Close the event loop."""
        self.loop.close()

    def test_is_owner_with_bot_is_owner_set_to_true(self):
        """
        Test is_owner() with bot.is_owner() set to True.

        checks.is_owner() should always return the same result
        as bot.is_owner(), in this case True.
        """
        self.ctx.bot.is_owner.return_value = True
        result = self.loop.run_until_complete(checks.is_owner(self.ctx))

        self.assertTrue(result)

    def test_is_owner_with_bot_is_owner_set_to_false(self):
        """
        Test is_owner() with bot.is_owner() set to False.

        checks.is_owner() should always return the same result
        as bot.is_owner(), in this case False.
        """
        self.ctx.bot.is_owner.return_value = False
        result = self.loop.run_until_complete(checks.is_owner(self.ctx))

        self.assertFalse(result)

    def test_is_mod_with_ctx_object_and_authorised_caller(self):
        """
        Test is_mod() with context object when caller is admin.

        Should return guild_permissions.administrator (== True).
        """
        self.member.guild_permissions.administrator = True
        result = self.loop.run_until_complete(checks.is_mod(self.ctx))

        self.assertTrue(result)

    def test_is_mod_with_ctx_object_and_unauthorised_caller(self):
        """
        Test is_mod() with context object when caller is NOT admin.

        Should return guild_permissions.administrator (== False).
        """
        self.member.guild_permissions.administrator = False
        result = self.loop.run_until_complete(checks.is_mod(self.ctx))

        self.ctx.send.assert_called_with(
            "@member Only mods are allowed to use that command.")
        self.assertFalse(result)

    def test_is_mod_with_ctx_object_and_unauthorised_caller_in_dm(self):
        """
        Test is_mod() with context object when caller is NOT admin.

        Should return guild_permissions.administrator (== False).
        """
        self.ctx.guild = None
        result = self.loop.run_until_complete(checks.is_mod(self.ctx))

        self.ctx.send.assert_called_with(
            "Don't you try to sneak into my DMs and mod me!")
        self.assertFalse(result)

    def test_is_mod_with_member_object_and_authorised_caller(self):
        """
        Test is_mod() with member object when caller is admin.

        Should return guild_permissions.administrator (== True).
        """
        self.member.guild_permissions.administrator = True
        result = self.loop.run_until_complete(checks.is_mod(self.member))

        self.assertTrue(result)

    def test_is_mod_with_member_object_and_unauthorised_caller(self):
        """
        Test is_mod() with member object when caller is NOT admin.

        Should return guild_permissions.administrator (== False).
        """
        self.member.guild_permissions.administrator = False
        result = self.loop.run_until_complete(checks.is_mod(self.member))

        self.assertFalse(result)

    def test_always_allow_with_regular_user(self):
        """
        Test always_allow() with non-owner non-admin member.

        Should return True.
        """
        self.ctx.bot.is_owner.return_value = False
        self.member.guild_permissions.administrator = False

        result = self.loop.run_until_complete(checks.always_allow(self.member))

        self.assertTrue(result)

    def test_always_allow_with_non_owner_admin(self):
        """
        Test always_allow() with non-owner admin member.

        Should return True.
        """
        self.ctx.bot.is_owner.return_value = False
        self.member.guild_permissions.administrator = True

        result = self.loop.run_until_complete(checks.always_allow(self.member))

        self.assertTrue(result)

    def test_always_allow_with_owner(self):
        """
        Test always_allow() with owner non-admin member.

        Should return True.
        """
        self.ctx.bot.is_owner.return_value = True
        self.member.guild_permissions.administrator = False

        result = self.loop.run_until_complete(checks.always_allow(self.member))

        self.assertTrue(result)

    def test_always_deny_with_regular_user(self):
        """
        Test always_deny() with non-owner non-admin member.

        Should return False.
        """
        self.ctx.bot.is_owner.return_value = False
        self.member.guild_permissions.administrator = False

        result = self.loop.run_until_complete(checks.always_deny(self.member))

        self.assertFalse(result)

    def test_always_deny_with_non_owner_admin(self):
        """
        Test always_deny() with non-owner admin member.

        Should return False.
        """
        self.ctx.bot.is_owner.return_value = False
        self.member.guild_permissions.administrator = True

        result = self.loop.run_until_complete(checks.always_deny(self.member))

        self.assertFalse(result)

    def test_always_deny_with_owner(self):
        """
        Test always_deny() with owner non-admin member.

        Should return False.
        """
        self.ctx.bot.is_owner.return_value = True
        self.member.guild_permissions.administrator = False

        result = self.loop.run_until_complete(checks.always_deny(self.member))

        self.assertFalse(result)
