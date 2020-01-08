"""Unittest for the greeting module."""

import io
import sys

from mrfreeze import colors
from mrfreeze import greeting

from tests import helpers


def test_greeting():
    """
    Verify that the greeting message is printed correctly.

    This only tests the information inside the box, not the coloring.
    All ANSI escape sequences are removed before testing.
    """
    bot = helpers.MockMrFreeze()
    bot.user.__str__ = lambda _: "BOT.USER #1234"
    bot.user.id = 1234567890
    bot.user.name = "BOT.USER.NAME"
    bot.guilds = [helpers.MockGuild()]
    bot.guilds[0].text_channels = [i for i in range(10)]
    bot.users = [i for i in range(30)]

    captured_output = io.StringIO()
    sys.stdout = captured_output
    greeting.bot_greeting(bot)
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue().splitlines()

    expected = [
        f"#######################################",
        f"# We have logged in as BOT.USER #1234 #",
        f"# User name:           BOT.USER.NAME  #",
        f"# User ID:             1234567890     #",
        f"# Number of servers:   1              #",
        f"# Number of channels:  10             #",
        f"# Number of users:     30             #",
        f"#######################################"
    ]

    for i in enumerate(expected):
        actual = colors.strip(output[i[0]])
        expected = i[1]
        assert expected, actual
