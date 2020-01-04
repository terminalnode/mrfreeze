"""Unittest for the greeting module."""
# TODO: strip color escape codes from output and verify
# output without the colors. This will make the test more
# meaningful since the colors are just cosmetic.

import io
import sys
import unittest

from mrfreeze import colors
from mrfreeze import greeting

from tests import helpers


class GreetingUnitTest(unittest.TestCase):
    """Unittest for the greeting module."""

    def test_greeting(self):
        """Verify that the greeting message is printed correctly."""
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

        self.maxDiff = None
        c = colors.CYAN
        b = colors.CYAN_B
        r = colors.RESET
        expected = [
            f"{c}#######################################{r}",
            f"{c}#{r} {c}{b}We have logged in as BOT.USER #1234 {c}#{r}",
            f"{c}#{r} {c}User name:           {b}BOT.USER.NAME  {c}#{r}",
            f"{c}#{r} {c}User ID:             {b}1234567890     {c}#{r}",
            f"{c}#{r} {c}Number of servers:   {b}1              {c}#{r}",
            f"{c}#{r} {c}Number of channels:  {b}10             {c}#{r}",
            f"{c}#{r} {c}Number of users:     {b}30             {c}#{r}",
            f"{c}#######################################{r}"
        ]
        for i in enumerate(expected):
            self.assertEqual(i[1], output[i[0]])
