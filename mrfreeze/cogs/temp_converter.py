"""Listener that detects and converts temperature statements."""

import re
from enum import Enum

import discord

from mrfreeze.cogs.cogbase import CogBase


class TempUnit(Enum):
    """Enumerator for the various temperature units."""

    C = "°C"
    K = "K"
    F = "°F"
    R = "°R"


def setup(bot):
    """Add the cog to the bot."""
    bot.add_cog(TemperatureConverter(bot))


class TemperatureConverter(CogBase):
    """Listener that detects and converts temperature statements."""

    def __init__(self, bot):
        """Initialize the cog."""
        self.bot = bot

    @CogBase.listener()
    async def on_message(self, message):
        """Look through all messages received for temperature statements."""
        if message.author.bot:
            return

        ctx = await self.bot.get_context(message)
        author = ctx.author.mention
        channel = ctx.channel

        # Abort if no temperature statement was found.
        statement = self.parse_request(ctx)
        if not statement:
            return

        # Check if input is ridiculously high/low.
        if abs(statement["temperature"]) >= 100000:
            hotcold = "a bit chilly"
            image_path = "images/hellacold.gif"

            if statement["temperature"] > 0:
                hotcold = "quite warm"
                image_path = "images/helldog.gif"

            await channel.send(
                    f"{author} No matter what unit you put that " +
                    f"in the answer is still gonna be \"{hotcold}\".",
                    file=discord.File(image_path))
            return

        # Calculate converted temperature,
        # see if it's above or equal to dog threshold.
        if statement["origin"] == TempUnit.C:
            new_temp = self.celsius_table(
                statement["temperature"],
                statement["destination"])
            in_c = statement["temperature"]

        elif statement["origin"] == TempUnit.F:
            new_temp = self.fahrenheit_table(
                statement["temperature"],
                statement["destination"])
            in_c = self.fahrenheit_table(statement["temperature"], TempUnit.C)

        elif statement["origin"] == TempUnit.K:
            new_temp = self.kelvin_table(
                statement["temperature"],
                statement["destination"])
            in_c = self.kelvin_table(statement["temperature"], TempUnit.C)

        else:  # Has to be rankine
            new_temp = self.rankine_table(
                statement["temperature"],
                statement["destination"])
            in_c = self.rankine_table(statement["temperature"], TempUnit.C)

        # hot/cold thresholds are defined in celsius
        image = None
        if in_c >= 35:
            image = discord.File("images/helldog.gif")
        elif in_c <= -20:
            image = discord.File("images/hellacold.gif")

        # old/new_temp contains the temperature values as floats.
        old_temp = round(statement["temperature"], 2)
        new_temp = round(new_temp, 2)
        # Check if old and new temp are the same temperatures or units.
        no_change = (old_temp == new_temp)
        same_unit = (statement["origin"] == statement["destination"])
        # Get the abbreviations for each temperature unit
        origin = statement["origin"].value
        destination = statement["destination"].value

        # Time for the reply.
        if no_change:
            if same_unit and statement["manual"]:
                reply = (f"Did {author} just try to convert {old_temp}" +
                         f"{origin} to {destination}? :thinking:")
            elif statement["manual"]:
                reply = (f"Uh... {old_temp}{origin} is the same in " +
                         f"{new_temp}{destination} you smud. :angry:")
            else:
                reply = (f"Guess what! {old_temp}{origin} is the same as " +
                         f"{new_temp}{destination}! WOOOW!")
        else:
            reply = f"{old_temp}{origin} is around {new_temp}{destination}"
        await channel.send(reply, file=image)

    def parse_request(self, ctx):
        """
        Extract temperature statement from text.

        If no temperature statement is found returns false.
        Otherwise returns a dictionary with keys:
            temperature, origin, destination, manual
        """
        text = ctx.message.content

        # Space or ° mandatory for kelvin to avoid
        # collision with k as in thousand.
        numbers = r"(?:(?:\s|^)-)?\d+(?:[,.]\d+)? ?"
        celsius = r"°?(?:c|celcius|celsius|civili[sz]ed units?)"
        fahrenheit = r"°?(?:f|fahrenheit|freedom units?)"
        degrees = r"°?(?:deg|degrees)"
        kelvin = r"(?:k|kelvin)"
        rankine = r"°?(?:r|rankine)"
        regex = (f"({numbers})(?:({celsius})|({fahrenheit})" +
                 fr"|([ °]{kelvin})|({rankine})|({degrees}))(?:\s|$)")
        statement = re.search(regex, text, re.IGNORECASE)
        if not statement:
            return False

        result = dict()

        # Determine the origin unit.
        statement = statement.groups()
        result["temperature"] = float(statement[0].replace(",", "."))
        if statement[1]:
            result["origin"] = TempUnit.C
        elif statement[2]:
            result["origin"] = TempUnit.F
        elif statement[3]:
            result["origin"] = TempUnit.K
        elif statement[4]:
            result["origin"] = TempUnit.R
        else:  # Has to be "degrees", needs to be converted into real unit
            if ctx.guild is not None:
                # Not DMs
                roles = ctx.author.roles
                if discord.utils.get(roles, name="Celsius"):
                    result["origin"] = TempUnit.C
                elif discord.utils.get(roles, name="Fahrenheit"):
                    result["origin"] = TempUnit.F
                elif discord.utils.get(roles, name="Canada"):
                    result["origin"] = TempUnit.C
                elif discord.utils.get(roles, name="Mexico"):
                    result["origin"] = TempUnit.C
                elif discord.utils.get(roles, name="North America"):
                    result["origin"] = TempUnit.F
                else:
                    # Default is celsius
                    result["origin"] = TempUnit.C
            else:
                # DMs
                result["origin"] = TempUnit.C

        # Determine destination unit
        # First we'll look for force conversions
        no_catch = (fr"(?:(?:{numbers}) ?(?:{celsius}|{fahrenheit}|" +
                    fr"{degrees}|[ °]{kelvin}|{rankine})) (?:for|in|as" +
                    fr"|(?:convert )?to|convert)")
        find_convert = (fr"{no_catch} (?:({celsius})|({fahrenheit})" +
                        fr"|(°?{kelvin})|({rankine}))(?:\s|$)")
        conversion = re.search(find_convert, text, re.IGNORECASE)

        if conversion:
            result["manual"] = True
            conversion = conversion.groups()
            if conversion[0]:
                result["destination"] = TempUnit.C
            elif conversion[1]:
                result["destination"] = TempUnit.F
            elif conversion[2]:
                result["destination"] = TempUnit.K
            else:  # Has to be rankine
                result["destination"] = TempUnit.R
        else:
            result['manual'] = False
            if result["origin"] == TempUnit.F:
                result["destination"] = TempUnit.C
            elif result["origin"] == TempUnit.K:
                result["destination"] = TempUnit.C
            elif result["origin"] == TempUnit.C:
                result["destination"] = TempUnit.F
            else:  # Has to be rankine
                result["destination"] = TempUnit.F

        return result

    def celsius_table(self, temp, dest):
        """Convert from celsius to other units."""
        if dest == TempUnit.C:
            return temp
        elif dest == TempUnit.F:
            return temp * 9.0 / 5.0 + 32
        elif dest == TempUnit.K:
            return temp + 273.15
        else:  # Has to be rankine
            return (temp + 273.15) * 9.0 / 5.0

    def fahrenheit_table(self, temp, dest):
        """Convert from fahrenheit to other units."""
        if dest == TempUnit.C:
            return (temp - 32) * 5.0 / 9.0
        elif dest == TempUnit.F:
            return temp
        elif dest == TempUnit.K:
            return (temp + 459.67) * 5.0 / 9.0
        else:  # Has to be rankine
            return temp + 459.67

    def kelvin_table(self, temp, dest):
        """Convert from kelvin to other units."""
        in_celsius = (temp - 273.15)
        return self.celsius_table(in_celsius, dest)

    def rankine_table(self, temp, dest):
        """Convert from rankine to other units."""
        in_fahrenheit = (temp - 459.67)
        return self.fahrenheit_table(in_fahrenheit, dest)
