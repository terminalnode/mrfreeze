"""Unittest for the command checks."""

import asyncio
import unittest

from mrfreeze import checks

from tests import helpers


class ChecksUnitTest(unittest.TestCase):
    """Test the command checks."""

    def setUp(self):
        """
        Set up a clean environment for each test.

        Each check takes a context object, except for is_mod
        which can take either a context object or a member object.
        """
        self.ctx = helpers.MockContext()
        self.member = self.ctx.author
        self.loop = asyncio.new_event_loop()

    def tearDown(self):
        """Close the event loop."""
        self.loop.close()

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
