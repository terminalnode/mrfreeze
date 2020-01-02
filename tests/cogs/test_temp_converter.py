"""Unittest for the TemperatureConverter cog."""

import asyncio
import unittest

from mrfreeze.cogs.temp_converter import TemperatureConverter

from tests import helpers


class TemperatureConverterCogUnitTest(unittest.TestCase):
    """Test the conversion tables in the TemperatureConverter cog."""

    def setUp(self):
        """Set up a clean environment for each test."""
        self.bot = helpers.MockMrFreeze()
        self.cog = TemperatureConverter(self.bot)

        self.msg = helpers.MockMessage()

        self.channel = self.msg.channel

        self.author = helpers.MockMember()
        self.author.bot = False
        self.msg.author = self.author

        self.ctx = helpers.MockContext()
        self.ctx.message = self.msg
        self.ctx.author = self.author
        self.ctx.channel = self.channel

        self.bot.get_context.return_value = self.ctx

        self.file = None

    def tearDown(self):
        """Ensure that all files are closed down."""
        if self.file is not None:
            self.file.close()

    def test_on_message_no_response_when_user_is_bot(self):
        """Test that on_message() does nothing when called by bot."""
        self.msg.author.bot = True
        coroutine = self.cog.on_message(self.msg)
        self.assertIsNone(asyncio.run(coroutine))
        self.channel.send.assert_not_called()

    def test_on_message_with_temperature_10000(self):
        """
        Test on_message() with message "10000 C".

        Should return a message saying that it's quite warm,
        and a picture of helldog.gif.
        """
        self.msg.content = "10000 C"
        coroutine = self.cog.on_message(self.msg)
        self.assertIsNone(asyncio.run(coroutine))
        result = self.channel.send.call_args[0][0]

        expected = ("@member No matter what unit you put that in " +
                    "the answer is still gonna be \"quite warm\".")
        self.assertEqual(expected, result)

    def test_on_message_with_temperature_negative_10000(self):
        """
        Test on_message() with message "-10000 C".

        Should return a message saying that it's a bit chilly,
        and a picture of hellacold.gif.
        """
        self.msg.content = "-10000 C"
        coroutine = self.cog.on_message(self.msg)
        self.assertIsNone(asyncio.run(coroutine))
        result = self.channel.send.call_args[0][0]

        expected = ("@member No matter what unit you put that in " +
                    "the answer is still gonna be \"a bit chilly\".")
        self.assertEqual(expected, result)

    def test_on_message_with_temperature_50_c(self):
        """
        Test on_message() with message "50 c".

        Should return a message saying 50 c is around 122 f.
        """
        self.msg.content = "50 c"
        coroutine = self.cog.on_message(self.msg)
        self.assertIsNone(asyncio.run(coroutine))
        result = self.channel.send.call_args[0][0]

        expected = ("50.0°C is around 122.0°F")
        self.assertEqual(expected, result)

    def test_on_message_with_temperature_50_f(self):
        """
        Test on_message() with message "50 f".

        Should return a message saying 50 f is around 10 c.
        """
        self.msg.content = "50 f"
        coroutine = self.cog.on_message(self.msg)
        self.assertIsNone(asyncio.run(coroutine))
        result = self.channel.send.call_args[0][0]

        expected = ("50.0°F is around 10.0°C")
        self.assertEqual(expected, result)

    def test_on_message_with_temperature_50_k(self):
        """
        Test on_message() with message "50 k".

        Should return a message saying 50 k is around -223.15 c.
        """
        self.msg.content = "50 k"
        coroutine = self.cog.on_message(self.msg)
        self.assertIsNone(asyncio.run(coroutine))
        result = self.channel.send.call_args[0][0]

        expected = ("50.0K is around -223.15°C")
        self.assertEqual(expected, result)

    def test_on_message_with_temperature_50_r(self):
        """
        Test on_message() with message "50 r".

        Should return a message saying 50 r is around -409.67 f.
        """
        self.msg.content = "50 r"
        coroutine = self.cog.on_message(self.msg)
        self.assertIsNone(asyncio.run(coroutine))
        result = self.channel.send.call_args[0][0]

        expected = ("50.0°R is around -409.67°F")
        self.assertEqual(expected, result)
