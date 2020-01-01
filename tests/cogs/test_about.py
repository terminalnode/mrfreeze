"""Unittest for the commands in the About cog."""

import asyncio
import unittest

import discord

from mrfreeze.cogs.about import About

from tests import helpers


class AboutCogUnitTest(unittest.TestCase):
    """Test the About cog."""

    def setUp(self):
        """Set up a clean environment for each test."""
        self.bot = helpers.MockMrFreeze()
        self.botname = "BOTNAME"
        self.bot_id = 1234567890
        self.bot.user.name = self.botname
        self.bot.user.id = self.bot_id

        self.cog = About(self.bot)

        self.ctx = helpers.MockContext()

        self.mrfreeze_blue = discord.Color(0x00dee9)

        self.file = None

    def tearDown(self):
        """Ensure that all files are closed down."""
        if self.file is not None:
            self.file.close()

    def test_readme_embed_and_file(self):
        """Test !readme in the About cog."""
        # Run and assert that it doesn't return anything
        # Assert that it was indeed called exactly once
        coroutine = self.cog.readme.callback(self.cog, self.ctx)
        self.assertIsNone(asyncio.run(coroutine))
        self.ctx.send.assert_called_once()
        _, kwargs = self.ctx.send.call_args

        # Assert that embed has the right color
        self.assertEqual(
            kwargs["embed"].color,
            self.mrfreeze_blue,
            msg="Embed color should be MrFreeze Blue")

        # Assert that embed has the right title
        self.assertEqual(
            kwargs["embed"].title,
            discord.Embed.Empty,
            msg="Embed title should be empty")

        # Assert that embed has the right description
        self.assertEqual(
                kwargs["embed"].title,
                discord.Embed.Empty,
                msg="Embed description should be empty")

        # Assert that embed has the right number of fields
        self.assertEqual(
            len(kwargs["embed"].fields),
            1,
            msg="Embed should only have one field")

        # Assert that embed field has the right title
        self.assertEqual(
            kwargs["embed"].fields[0].name,
            "Readme")

        # Assert that embed has the right text
        self.assertEqual(
            kwargs["embed"].fields[0].value,
            ("My readme file is available [on Github](https://" +
             "github.com/terminalnode/mrfreeze/blob/master/README.md)!"))

        # Assert that file name is correct
        self.assertEqual(
            kwargs["file"].filename,
            "readme.png")

        # Assert that the file is readable
        self.assertTrue(kwargs["file"].fp.readable())
        self.file = kwargs["file"]

    def test_source_embed_and_file(self):
        """Test !source in the About cog."""
        # Run and assert that it doesn't return anything
        # Assert that it was indeed called exactly once
        coroutine = self.cog.source.callback(self.cog, self.ctx)
        self.assertIsNone(asyncio.run(coroutine))
        self.ctx.send.assert_called_once()
        _, kwargs = self.ctx.send.call_args

        # Assert that embed has the right color
        self.assertEqual(
            kwargs["embed"].color,
            self.mrfreeze_blue,
            msg="Embed color should be MrFreeze Blue")

        # Assert that embed has the right title
        self.assertEqual(
            kwargs["embed"].title,
            discord.Embed.Empty,
            msg="Embed title should be empty")

        # Assert that embed has the right description
        self.assertEqual(
            kwargs["embed"].description,
            discord.Embed.Empty,
            msg="Embed description should be empty")

        # Assert that embed has the right number of fields
        self.assertEqual(
            len(kwargs["embed"].fields),
            1,
            msg="Embed should only have one field")

        # Assert that embed field has the right title
        self.assertEqual(
            kwargs["embed"].fields[0].name,
            "Source code")

        # Assert that embed field has the right text
        embed_text = "My source code is available [on Github]"
        embed_text += "(https://github.com/terminalnode/mrfreeze)!"
        self.assertEqual(
            kwargs["embed"].fields[0].value,
            embed_text)

        # Assert that file name is correct and file is readable
        self.assertEqual(
            kwargs["file"].filename,
            "source.png",
            msg="!source image should be source.png")

        # Assert that the file is readable
        self.assertTrue(kwargs["file"].fp.readable())
        self.file = kwargs["file"]

    def test_getfreeze_embed_and_file(self):
        """Test !getfreeze in the About cog."""
        # Run and assert that it doesn't return anything
        # Assert that it was indeed called exactly once
        coroutine = self.cog.getfreeze.callback(self.cog, self.ctx)
        self.assertIsNone(asyncio.run(coroutine))
        self.ctx.send.assert_called_once()
        _, kwargs = self.ctx.send.call_args

        # Assert that embed has the right color
        self.assertEqual(
            kwargs["embed"].color,
            self.mrfreeze_blue,
            msg="Embed color should be MrFreeze Blue")

        # Assert that embed has the right title
        self.assertEqual(
            kwargs["embed"].title,
            discord.Embed.Empty,
            msg="Embed title should be empty")

        # Assert that embed has the right description
        embed_desc = "Here's a link for inviting me, **BOTNAME**, to a server."
        embed_desc += "The link will invite *this* version of me, be it the "
        embed_desc += "beta or regular version. Not the impostor.\n\nNote "
        embed_desc += "however that **!banish** and **!region** won't work "
        embed_desc += "without the right server infrastructure (roles etc.)."
        self.assertEqual(
            kwargs["embed"].description,
            embed_desc,
            msg="Embed description/text is wrong")

        # Assert that embed has the right number of fields
        self.assertEqual(
            len(kwargs["embed"].fields),
            1,
            msg="Embed should only have one field")

        # Assert that embed field has the right title
        self.assertEqual(
            kwargs["embed"].fields[0].name,
            "Invite link for BOTNAME",
            msg="embed field[0] has the wrong name.")

        # Assert that embed field has the right value
        bot_url = "https://discordapp.com/oauth2/authorize?client_id="
        bot_url += f"{self.bot_id}&scope=bot"
        self.assertEqual(
            kwargs["embed"].fields[0].value,
            f"[Invite BOTNAME to a server]({bot_url})")

        # Assert that bot avatar was retrieved as png
        _, avatar_url_call = self.bot.user.avatar_url_as.call_args
        self.assertEqual(
            avatar_url_call,
            {"static_format": "png"})

    def test_dummies(self):
        """Test !dummies in the About cog."""
        # Run and assert that it doesn't return anything
        # Assert that it was indeed called exactly once
        coroutine = self.cog.dummies.callback(self.cog, self.ctx)
        self.assertIsNone(asyncio.run(coroutine))
        self.ctx.send.assert_called_once()
        _, kwargs = self.ctx.send.call_args

        # Assert that embed has the right color
        self.assertEqual(
            kwargs["embed"].color,
            self.mrfreeze_blue,
            msg="Embed color should be MrFreeze Blue")

        # Assert that embed has the right title
        self.assertEqual(
            kwargs["embed"].title,
            discord.Embed.Empty,
            "Embed title should be empty")

        # Assert that embed has the right description
        desc = "Here are the links for inviting Ba'athman and Robin, "
        desc += "my arch enemies, to a server.\n\nThey don't do anything "
        desc += "whatsoever, but are very useful for testing purposes "
        desc += "such as trying out kick and ban commands."

        self.assertEqual(
            kwargs["embed"].description,
            desc,
            msg="Embed description is wrong")

        # Assert that embed has the right number of fields
        self.assertEqual(
            len(kwargs["embed"].fields),
            1,
            msg="Embed should only have one field")

        # Assert that embed field has the right title
        self.assertEqual(
            kwargs["embed"].fields[0].name,
            "Dummy Bots",
            msg="Field name should be 'Dummy Bots'")

        # Assert that embed field has the right text
        baathman_url = "https://discordapp.com/oauth2/authorize?"
        baathman_url += "client_id=469030362119667712&scope=bot"
        robin_url = "https://discordapp.com/oauth2/authorize?"
        robin_url += "client_id=469030900492009472&scope=bot"
        field_txt = f"[Invite Ba'athman to a server]({baathman_url})\n"
        field_txt += f"[Invite Robin to a server]({robin_url})"
        self.assertEqual(
            kwargs["embed"].fields[0].value,
            field_txt)

        # Assert that file name is correct
        self.assertEqual(
            kwargs["file"].filename,
            "dummies.png",
            msg="!dummies image should be dummies.png")

        # Assert that the file is readable
        self.assertTrue(kwargs["file"].fp.readable())
        self.file = kwargs["file"]

    def test_todo(self):
        """Test !todo in the About cog."""
        # Run and assert that it doesn't return anything
        # Assert that it was indeed called exactly once
        coroutine = self.cog.todos.callback(self.cog, self.ctx)
        self.assertIsNone(asyncio.run(coroutine))
        self.ctx.send.assert_called_once()
        _, kwargs = self.ctx.send.call_args

        # Assert that embed has the right color
        self.assertEqual(
            kwargs["embed"].color,
            self.mrfreeze_blue,
            msg="Embed color should be MrFreeze Blue")

        # Assert that embed has the right title
        self.assertEqual(
            kwargs["embed"].title,
            discord.Embed.Empty,
            "Embed title should be empty")

        # Assert that embed has the right description
        self.assertEqual(
            kwargs["embed"].description,
            discord.Embed.Empty,
            "Embed description should be empty")

        # Assert that embed has the right number of fields
        self.assertEqual(
            len(kwargs["embed"].fields),
            1,
            msg="Embed should only have one field")

        # Assert that embed field has the right title
        self.assertEqual(
            kwargs["embed"].fields[0].name,
            "TODO list",
            msg="Field name should be 'TODO list'")

        # Assert that embed field has the right text
        field_txt = "You're a nosy one! [Here](https://github.com/terminalnode"
        field_txt += "/mrfreeze/blob/master/TODO.md)'s a list of all the "
        field_txt += "\"cool\" stuff Terminal has planned for me... :sleeping:"
        self.assertEqual(
            kwargs["embed"].fields[0].value,
            field_txt)

        # Assert that file name is correct
        self.assertEqual(
            kwargs["file"].filename,
            "todos.png",
            msg="!todo image should be todos.png")

        # Assert that the file is readable
        self.assertTrue(kwargs["file"].fp.readable())
        self.file = kwargs["file"]
