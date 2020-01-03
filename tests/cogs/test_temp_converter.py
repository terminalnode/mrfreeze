"""Unittest for the TemperatureConverter cog."""

import asyncio
import unittest
from typing import List

from discord import File

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

        self.files: List[File] = list()

    def tearDown(self):
        """Ensure that all files are closed down."""
        for attachment in self.files:
            attachment.close()

    def call_on_ready_with(self, content: str) -> str:
        """
        Set msg.content to content and run on_ready().

        This is used by almost every test in this file, so it makes
        sense to break it out as a helper function. If a file was
        attached to the file self.file is set to point to this file
        to ensure that it's closed after the test finish running.
        """
        self.msg.content = content
        coroutine = self.cog.on_message(self.msg)
        self.assertIsNone(asyncio.run(coroutine))

        text, kwargs = self.channel.send.call_args

        attachment = kwargs.get("file")
        if attachment is not None:
            self.files.append(attachment)

        return text[0]

    def add_role_with_name(self, name: str):
        """Append a new role to author."""
        new_role = helpers.MockRole(name=name)
        self.author.roles.append(new_role)

    def test_on_message_no_response_when_user_is_bot(self):
        """Test that on_message() does nothing when called by bot."""
        self.msg.author.bot = True

        self.msg.content = "10 c"
        coroutine = self.cog.on_message(self.msg)
        self.assertIsNone(asyncio.run(coroutine))
        self.channel.send.assert_not_called()

    def test_on_message_no_response_with_invalid_statement(self):
        """
        Test on_message() with invalid temperature statement.

        Should return nothing at all.
        """
        self.msg.content = "10"
        coroutine = self.cog.on_message(self.msg)
        self.assertIsNone(asyncio.run(coroutine))
        self.channel.send.assert_not_called()

    def test_on_message_with_temperature_100000(self):
        """
        Test on_message() with message "100000 C".

        Should return a message saying that it's quite warm,
        and a picture of helldog.gif.
        """
        result = self.call_on_ready_with("100000 C")

        expected = ("@member No matter what unit you put that in " +
                    "the answer is still gonna be \"quite warm\".")
        self.assertEqual(expected, result)

    def test_on_message_with_temperature_negative_100000(self):
        """
        Test on_message() with message "-100000 C".

        Should return a message saying that it's a bit chilly,
        and a picture of hellacold.gif.
        """
        result = self.call_on_ready_with("-100000 C")

        expected = ("@member No matter what unit you put that in " +
                    "the answer is still gonna be \"a bit chilly\".")
        self.assertEqual(expected, result)

    def test_on_message_with_temperature_50_c(self):
        """
        Test on_message() with message "50 c".

        Should return a message saying 50 c is around 122 f.
        """
        result = self.call_on_ready_with("50 c")

        expected = ("50.0°C is around 122.0°F")
        self.assertEqual(expected, result)

    def test_on_message_with_temperature_50_f(self):
        """
        Test on_message() with message "50 f".

        Should return a message saying 50 f is around 10 c.
        """
        result = self.call_on_ready_with("50 f")

        expected = ("50.0°F is around 10.0°C")
        self.assertEqual(expected, result)

    def test_on_message_with_temperature_50_k(self):
        """
        Test on_message() with message "50 k".

        Should return a message saying 50 k is around -223.15 c.
        """
        result = self.call_on_ready_with("50 k")

        expected = ("50.0K is around -223.15°C")
        self.assertEqual(expected, result)

    def test_on_message_with_temperature_50_r(self):
        """
        Test on_message() with message "50 r".

        Should return a message saying 50 r is around -409.67 f.
        """
        result = self.call_on_ready_with("50.0 r")

        expected = ("50.0°R is around -409.67°F")
        self.assertEqual(expected, result)

    def test_on_message_degrees_with_no_role(self):
        """
        Test on_message() with message "50 degrees" and no role.

        Should assume origin unit is celsius.
        """
        result = self.call_on_ready_with("50,0 degrees")

        expected = "50.0°C is around 122.0°F"
        self.assertEqual(expected, result)

    def test_on_message_degrees_from_dm_channel(self):
        """
        Test on_message() when sent from DMs.

        Should assume origin unit is celsius, regardless of roles.
        Roles are not accessible in DM channels, but our mock object
        can have them to ensure that the roles are not accessed.
        """
        self.ctx.guild = None
        self.add_role_with_name("North America")
        result = self.call_on_ready_with("50 degrees")

        expected = "50.0°C is around 122.0°F"
        self.assertEqual(expected, result)

    def test_on_message_degrees_with_celsius_role(self):
        """
        Test on_message() with message "50 degrees" and Celsius role.

        Should assume origin unit is celsius.
        North America role is added to make sure the role does something.
        """
        self.add_role_with_name("Celsius")
        self.add_role_with_name("North America")
        result = self.call_on_ready_with("50 degrees")

        expected = "50.0°C is around 122.0°F"
        self.assertEqual(expected, result)

    def test_on_message_degrees_with_fahrenheit_role(self):
        """
        Test on_message() with message "50 degrees" and Fahrenheit role.

        Should assume origin unit is fahrenheit.
        """
        self.add_role_with_name("Fahrenheit")
        result = self.call_on_ready_with("50 Degrees")

        expected = "50.0°F is around 10.0°C"
        self.assertEqual(expected, result)

    def test_on_message_degrees_with_canada_role(self):
        """
        Test on_message() with message "50 degrees" and Canada role.

        Should assume origin unit is celsius.
        North America role is added to make sure the role does something.
        """
        self.add_role_with_name("Canada")
        self.add_role_with_name("North America")
        result = self.call_on_ready_with("50degrees")

        expected = "50.0°C is around 122.0°F"
        self.assertEqual(expected, result)

    def test_on_message_degrees_with_mexico_role(self):
        """
        Test on_message() with message "50 degrees" and Mexico role.

        Should assume origin unit is celsius.
        North America role is added to make sure the role does something.
        """
        self.add_role_with_name("Mexico")
        self.add_role_with_name("North America")
        result = self.call_on_ready_with("50 DEGREES")

        expected = "50.0°C is around 122.0°F"
        self.assertEqual(expected, result)

    def test_on_message_degrees_with_north_america_role(self):
        """
        Test on_message() with message "50 degrees" and North America role.

        Should assume origin unit is fahrenheit.
        """
        self.add_role_with_name("North America")
        result = self.call_on_ready_with("50 deg")

        expected = "50.0°F is around 10.0°C"
        self.assertEqual(expected, result)

    def test_on_message_celsius_aliases(self):
        """
        Test on_message() with various celsius aliases.

        Aliases are:
        °c, c, celcius, celsius, civilized unit(s), civilized unit(s).

        All of these should assume celsius.
        """
        self.add_role_with_name("Fahrenheit")
        aliases: List[str] = list()
        aliases.append("°c")
        aliases.append("c")
        aliases.append("celcius")
        aliases.append("celsius")
        aliases.append("civilized unit")
        aliases.append("civilized units")
        aliases.append("civilised unit")
        aliases.append("civilised units")

        expected = "50.0°C is around 122.0°F"
        for alias in aliases:
            self.assertEqual(
                expected,
                self.call_on_ready_with(f"50 {alias}"),
                msg=f"Used 50 {alias} as input.")

    def test_on_message_fahrenheit_aliases(self):
        """
        Test on_message() with various fahrenheit aliases.

        Aliases are:
        °f, f, fahrenheit, freedom unit, freedom units
        """
        self.add_role_with_name("Celsius")
        aliases: List[str] = list()
        aliases.append("°f")
        aliases.append("f")
        aliases.append("fahrenheit")
        aliases.append("freedom unit")
        aliases.append("freedom units")

        expected = "50.0°F is around 10.0°C"
        for alias in aliases:
            self.assertEqual(
                expected,
                self.call_on_ready_with(f"50{alias}"),
                msg=f"Used 50 {alias} as input.")

    def test_on_message_kelvin_aliases(self):
        """
        Test on_message() with various kelvin aliases.

        Aliases are:
        k, kelvin
        """
        aliases: List[str] = list()
        aliases.append("k")
        aliases.append("kelvin")

        expected = "50.0K is around -223.15°C"
        for alias in aliases:
            self.assertEqual(
                expected,
                self.call_on_ready_with(f"50 {alias}"),
                msg=f"Used 50 {alias} as input.")

    def test_on_message_rankine_aliases(self):
        """
        Test on_message() with various rankine aliases.

        Aliases are:
        r, rankine
        """
        aliases: List[str] = list()
        aliases.append("r")
        aliases.append("rankine")

        expected = "50.0°R is around -409.67°F"
        for alias in aliases:
            self.assertEqual(
                expected,
                self.call_on_ready_with(f"50 {alias}"),
                msg=f"Used 50 {alias} as input.")

    def test_on_message_forced_c_to_f(self):
        """
        Test on_message() when forcing conversion from c to f.

        Should return 50.0°C in fahrenheit.
        """
        self.add_role_with_name("Fahrenheit")
        result = self.call_on_ready_with("convert 50 c to f")

        expected = "50.0°C is around 122.0°F"
        self.assertEqual(expected, result)

    def test_on_message_forced_c_to_k(self):
        """
        Test on_message() when forcing conversion from c to k.

        Should return 50.0°C in kelvin.
        """
        result = self.call_on_ready_with("50 degrees in k")

        expected = "50.0°C is around 323.15K"
        self.assertEqual(expected, result)

    def test_on_message_forced_c_to_r(self):
        """
        Test on_message() when forcing conversion from c to r.

        Should return 50.0°C in rankine.
        """
        result = self.call_on_ready_with("50 deg as rankine")

        expected = "50.0°C is around 581.67°R"
        self.assertEqual(expected, result)

    def test_on_message_forced_f_to_k(self):
        """
        Test on_message() when forcing conversion from f to k.

        Should return 50.0°F in kelvin.
        """
        result = self.call_on_ready_with("50 f for kelvin")

        expected = "50.0°F is around 283.15K"
        self.assertEqual(expected, result)

    def test_on_message_forced_f_to_r(self):
        """
        Test on_message() when forcing conversion from f to r.

        Should return 50.0°F in rankine.
        """
        result = self.call_on_ready_with("50 f as RANKINE")

        expected = "50.0°F is around 509.67°R"
        self.assertEqual(expected, result)

    def test_on_message_forced_k_to_f(self):
        """
        Test on_message() when forcing conversion from k to f.

        Should return 50.0K in fahrenheit.
        """
        result = self.call_on_ready_with("50 k convert to f")

        expected = "50.0K is around -369.67°F"
        self.assertEqual(expected, result)

    def test_on_message_forced_r_to_c(self):
        """
        Test on_message() when forcing conversion from r to c.

        Should return 50°R in celsius.
        """
        result = self.call_on_ready_with("50 r to c")

        expected = "50.0°R is around -245.37°C"
        self.assertEqual(expected, result)

    def test_on_message_forced_c_to_c(self):
        """
        Test on_message() when forcing conversion from c to c.

        Should return:
        "Did {author} just try to convert {old_temp} {origin}
         to {destination}? :thinking:"
        """
        result = self.call_on_ready_with("50 c in c")

        expected = "Did @member just try to convert 50.0°C to °C? :thinking:"
        self.assertEqual(expected, result)

    def test_on_message_when_original_and_converted_are_same_not_forced(self):
        """
        Test on_message() with -40 C and non-forced conversion.

        Should return a surprised exclamation saying that they are the same.
        Should also have hellacold.gif attached.
        """
        result = self.call_on_ready_with("-40 c")

        expected = "Guess what! -40.0°C is the same as -40.0°F! WOOOW!"
        self.assertEqual(expected, result)

    def test_on_message_when_original_and_converted_are_same_forced(self):
        """
        Test on_message() with -40 C and forced conversion to fahrenheit.

        Should return an angry response saying that they are the same,
        and that the author knew they would be.
        """
        result = self.call_on_ready_with("-40 c in f")

        expected = "Uh... -40.0°C is the same in -40.0°F you smud. :angry:"
        self.assertEqual(expected, result)

    def test_on_message_with_temperature_minus_20c_gives_gif(self):
        """
        Verify that on_message() with -20c includes hellacold.gif in output.

        -20c is the threshold for including the gif. It should be included
        in the response for this request.
        """
        self.call_on_ready_with("-20.0 c")

        self.assertEqual(
            len(self.files),
            1, msg="self.files should have exactly one file.")

        gif = self.files[0]
        self.assertEqual(
            gif.filename,
            "hellacold.gif")

        self.assertTrue(
            gif.fp.readable(),
            msg="File is not readable")

    def test_on_message_with_temperature_minus_19c_gives_no_gif(self):
        """
        Verify that on_message() with -19c doesn't include gif in output.

        -20c is the threshold for including the gif. -19c should not have
        any attachments whatsoever.
        """
        self.call_on_ready_with("-19.0 c")

        self.assertEqual(
            len(self.files),
            0, msg="self.files should be empty.")

    def test_on_message_with_temperature_35c_gives_gif(self):
        """
        Verify that on_message() with 35c includes helldog.gif in output.

        35c is the threshold for including the gif. It should be included
        in the response for this request.
        """
        self.call_on_ready_with("35.0 c")

        self.assertEqual(
            len(self.files),
            1, msg="self.files should have exactly one file.")

        gif = self.files[0]
        self.assertEqual(
            gif.filename,
            "helldog.gif")

        self.assertTrue(
            gif.fp.readable(),
            msg="File is not readable")

    def test_on_message_with_temperature_34c_gives_no_gif(self):
        """
        Verify that on_message() with 34c doesn't include gif in output.

        35c is the threshold for including the gif. 34c should not have
        any attachments whatsoever.
        """
        self.call_on_ready_with("34.0 c")

        self.assertEqual(
            len(self.files),
            0, msg="self.files should be empty.")
