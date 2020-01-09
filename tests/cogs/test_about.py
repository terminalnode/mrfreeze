"""Unittest for the commands in the About cog."""

import asyncio

import discord

from mrfreeze.cogs.about import About

import pytest

from tests import helpers

botname = "BOTNAME"
bot_id = 1234567890
mrfreeze_blue = discord.Color(0x00dee9)


@pytest.fixture()
def bot():
    """Create a MockMrFreeze object."""
    bot = helpers.MockMrFreeze()
    bot.user.name = botname
    bot.user.id = bot_id
    yield bot


@pytest.fixture()
def cog(bot):
    """Instantiate the cog."""
    yield About(bot)


@pytest.fixture()
def ctx():
    """Create a MockContext object."""
    yield helpers.MockContext()


def test_readme_embed_and_file(cog, ctx):
    """Test !readme in the About cog."""
    # Run and assert that it doesn't return anything
    # Assert that it was indeed called exactly once
    coroutine = cog.readme.callback(cog, ctx)
    assert asyncio.run(coroutine) is None

    ctx.send.assert_called_once()
    _, kwargs = ctx.send.call_args
    embed = kwargs["embed"]
    efile = kwargs["file"]

    # Assert that embed has the right color
    test = embed.color == mrfreeze_blue
    assert test, "!readme embed color should be MrFreeze Blue"

    # Assert that embed has the right title
    test = embed.title == discord.Embed.Empty
    assert test, "!readme embed title should be empty"

    # Assert that embed has the right description
    test = embed.description == discord.Embed.Empty
    assert test, "!readme embed description should be empty"

    # Assert that embed has the right number of fields
    test = len(embed.fields) == 1
    assert test, "!readme embed should only have one field"

    # Assert that embed field has the right title
    test = embed.fields[0].name == "Readme"
    assert test, "!readme embed title should be 'Readme'"

    # Assert that embed has the right text
    text = "My readme file is available [on Github]"
    text += "(https://github.com/terminalnode/mrfreeze/blob/master/README.md)!"

    test = embed.fields[0].value == text
    assert test, "!readme embed field has the wrong text"

    # Assert that file name is correct
    test = efile.filename == "readme.png"
    assert test, "!readme embed filename should be 'readme.png'"

    # Assert that the file is readable
    test = efile.fp.readable()
    assert test, "!readme embed file is not readable"


def test_source_embed_and_file(cog, ctx):
    """Test !source in the About cog."""
    # Run and assert that it doesn't return anything
    # Assert that it was indeed called exactly once
    coroutine = cog.source.callback(cog, ctx)
    assert asyncio.run(coroutine) is None

    ctx.send.assert_called_once()
    _, kwargs = ctx.send.call_args
    embed = kwargs["embed"]
    efile = kwargs["file"]

    # Assert that embed has the right color
    test = embed.color == mrfreeze_blue
    assert test, "!source embed color should be MrFreeze Blue"

    # Assert that embed has the right title
    test = embed.title == discord.Embed.Empty
    assert test, "!source embed title should be empty"

    # Assert that embed has the right description
    test = embed.description == discord.Embed.Empty
    assert test, "!source embed description should be empty"

    # Assert that embed has the right number of fields
    test = len(embed.fields) == 1
    assert test, "!source embed should only have one field"

    # Assert that embed field has the right title
    test = embed.fields[0].name == "Source code"
    assert test, "!source embed title should be 'Source code'"

    # Assert that embed field has the right text
    text = "My source code is available [on Github]"
    text += "(https://github.com/terminalnode/mrfreeze)!"

    test = embed.fields[0].value == text
    assert test, "!source embed field has the wrong text"

    # Assert that file name is correct and file is readable
    test = efile.filename == "source.png"
    assert test, "!source image should be source.png"

    # Assert that the file is readable
    test = efile.fp.readable()
    assert test, "!source embed file is not readable"


def test_getfreeze_embed_and_file(cog, ctx, bot):
    """Test !getfreeze in the About cog."""
    # Run and assert that it doesn't return anything
    # Assert that it was indeed called exactly once
    coroutine = cog.getfreeze.callback(cog, ctx)
    assert asyncio.run(coroutine) is None

    ctx.send.assert_called_once()
    _, kwargs = ctx.send.call_args
    embed = kwargs["embed"]

    # Assert that embed has the right color
    test = embed.color == mrfreeze_blue
    assert test, "!getfreeze embed color should be MrFreeze Blue"

    # Assert that embed has the right title
    test = embed.title == discord.Embed.Empty
    assert test, "!getfreeze embed title should be empty"

    # Assert that embed has the right description
    desc = "Here's a link for inviting me, **BOTNAME**, to a server."
    desc += "The link will invite *this* version of me, be it the "
    desc += "beta or regular version. Not the impostor.\n\nNote "
    desc += "however that **!banish** and **!region** won't work "
    desc += "without the right server infrastructure (roles etc.)."

    test = embed.description == desc
    assert test, "!getfreeze embed description is wrong"

    # Assert that embed has the right number of fields
    test = len(embed.fields) == 1
    assert test, "!getfreeze embed should only have one field"

    # Assert that embed field has the right title
    test = embed.fields[0].name == "Invite link for BOTNAME"
    assert test, "!getfreeze embed title should be 'Invite link for BOTNAME'"

    # Assert that embed field has the right value
    url = "[Invite BOTNAME to a server](https://discordapp.com/"
    url += f"oauth2/authorize?client_id={bot_id}&scope=bot)"

    test = embed.fields[0].value == url
    assert test, "!getfreeze embed field has the wrong text"

    # Assert that bot avatar was retrieved as png
    _, avatar_url_call = bot.user.avatar_url_as.call_args
    test = avatar_url_call == {"static_format": "png"}
    assert test, "!getfreeze embed file is not readable"


def test_dummies(cog, ctx):
    """Test !dummies in the About cog."""
    # Run and assert that it doesn't return anything
    # Assert that it was indeed called exactly once
    coroutine = cog.dummies.callback(cog, ctx)
    assert asyncio.run(coroutine) is None

    ctx.send.assert_called_once()
    _, kwargs = ctx.send.call_args
    embed = kwargs["embed"]
    efile = kwargs["file"]

    # Assert that embed has the right color
    test = embed.color == mrfreeze_blue
    assert test, "!dummies embed color should be MrFreeze Blue"

    # Assert that embed has the right title
    test = embed.title == discord.Embed.Empty
    assert test, "!dummies embed title should be empty"

    # Assert that embed has the right description
    desc = "Here are the links for inviting Ba'athman and Robin, "
    desc += "my arch enemies, to a server.\n\nThey don't do anything "
    desc += "whatsoever, but are very useful for testing purposes "
    desc += "such as trying out kick and ban commands."

    test = embed.description == desc
    assert test, "!dummies embed description is wrong"

    # Assert that embed has the right number of fields
    test = len(embed.fields) == 1
    assert test, "!dummies embed should only have one field"

    # Assert that embed field has the right title
    test = embed.fields[0].name == "Dummy Bots"
    assert test, "!dummies embed title should be 'Dummy Bots'"

    # Assert that embed field has the right text
    baathman_url = "https://discordapp.com/oauth2/authorize?"
    baathman_url += "client_id=469030362119667712&scope=bot"
    robin_url = "https://discordapp.com/oauth2/authorize?"
    robin_url += "client_id=469030900492009472&scope=bot"
    field_txt = f"[Invite Ba'athman to a server]({baathman_url})\n"
    field_txt += f"[Invite Robin to a server]({robin_url})"

    test = embed.fields[0].value == field_txt
    assert test, "!dummies embed field has the wrong text"

    # Assert that file name is correct
    test = efile.filename == "dummies.png"
    assert test, "!dummies image should be 'dummies.png'"

    # Assert that the file is readable
    test = efile.fp.readable()
    assert test, "!dummies embed file is not readable"


def test_todo(cog, ctx):
    """Test !todo in the About cog."""
    # Run and assert that it doesn't return anything
    # Assert that it was indeed called exactly once
    coroutine = cog.todos.callback(cog, ctx)
    assert asyncio.run(coroutine) is None

    ctx.send.assert_called_once()
    _, kwargs = ctx.send.call_args
    embed = kwargs["embed"]
    efile = kwargs["file"]

    # Assert that embed has the right color
    test = embed.color == mrfreeze_blue
    assert test, "!todo embed color should be MrFreeze Blue"

    # Assert that embed has the right title
    test = embed.title == discord.Embed.Empty
    assert test, "!todo embed title should be empty"

    # Assert that embed has the right description
    test = embed.description == discord.Embed.Empty
    assert test, "!todo embed description should be empty"

    # Assert that embed has the right number of fields
    test = len(embed.fields) == 1
    assert test, "!todo embed should only have one field"

    # Assert that embed field has the right title
    test = embed.fields[0].name == "TODO list"
    assert test, "!todo embed title should be 'TODO list'"

    # Assert that embed field has the right text
    field_txt = "You're a nosy one! [Here](https://github.com/terminalnode"
    field_txt += "/mrfreeze/blob/master/TODO.md)'s a list of all the "
    field_txt += "\"cool\" stuff Terminal has planned for me... :sleeping:"

    test = embed.fields[0].value == field_txt
    assert test, "!todo embed field has the wrong text"

    # Assert that file name is correct
    test = efile.filename == "todos.png"
    assert test, "!todo image should be 'todos.png'"

    # Assert that the file is readable
    test = efile.fp.readable()
    assert test, "!todo embed file is not readable"
