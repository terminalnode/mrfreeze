"""Unittest for the commands in the About cog."""

import asyncio
import unittest

import discord

from mrfreeze.cogs.about import About

from tests import helpers


# TODO Create context mock object

class AboutCogUnitTest(unittest.TestCase):
    """Test the About cog."""

    def setUp(self):
        """Set up a clean environment for each test."""
        self.bot = helpers.MockMrFreeze()
        self.cog = About(self.bot)
        self.ctx = helpers.MockContext()
        self.mrfreeze_blue = discord.Color(0x00dee9)

    def test_readme(self):
        """Test !readme in the About cog."""
        # Run and assert that it doesn't return anything
        # Assert that it was indeed called exactly once
        coroutine = self.cog.readme.callback(self.cog, self.ctx)
        self.assertIsNone(asyncio.run(coroutine))
        self.ctx.send.assert_called_once()

        # Extract kwargs
        _, kwargs = self.ctx.send.call_args

        # Assert that embed is correct
        self.assertEqual(kwargs["embed"].color, self.mrfreeze_blue)
        self.assertEqual(
            kwargs["embed"].fields[0].name,
            "Readme")
        self.assertEqual(
            kwargs["embed"].fields[0].value,
            ("My readme file is available [on Github](https://" +
             "github.com/terminalnode/mrfreeze/blob/master/README.md)!"))

        # Assert that file is correct and file is readable
        self.assertEqual(
            kwargs["file"].filename,
            "readme.png")
        self.assertTrue(kwargs["file"].fp.readable())

    def test_source(self):
        """Test !source in the About cog."""
        # Run and assert that it doesn't return anything
        # Assert that it was indeed called exactly once
        coroutine = self.cog.source.callback(self.cog, self.ctx)
        self.assertIsNone(asyncio.run(coroutine))
        self.ctx.send.assert_called_once()

        # Extract kwargs
        _, kwargs = self.ctx.send.call_args

        # Assert that embed is correct
        self.assertEqual(kwargs["embed"].color, self.mrfreeze_blue)
        self.assertEqual(
            kwargs["embed"].fields[0].name,
            "Source code")
        self.assertEqual(
            kwargs["embed"].fields[0].value,
            ("My source code is available [on Github](https://" +
             "github.com/terminalnode/mrfreeze)!"))

        # Assert that file name is correct and file is readable
        self.assertEqual(
            kwargs["file"].filename,
            "source.png")
        self.assertTrue(kwargs["file"].fp.readable())
