import discord          # Basic discord functionality.
import re               # Used extensively to parse input.
from enum import Enum   # Used to denote temperature units.
from mrfreeze.cogs.cogbase import CogBase

# Set to true to enable some printouts on how
# the temperature statement has been parsed.
TEMP_DEBUG = False


class TempUnit(Enum):
    # Kelvin is weird and doesn't use ° as a prefix.
    C = "°C"
    K = "K"
    F = "°F"
    R = "°R"


def setup(bot):
    """Add the cog to the bot."""
    bot.add_cog(TemperatureConverter(bot))


class TemperatureConverter(CogBase):
    """How the bot acts when messages are posted."""
    def __init__(self, bot):
        self.bot = bot

    # Certain events, namely temp, depends on checking for
    # temperature statements in all messages sent to the chat.
    @CogBase.listener()
    async def on_message(self, message):
        # Ignore what all the bots say...
        if message.author.bot:
            return

        # Look for temperature statements and autoconvert them.
        ctx = await self.bot.get_context(message)
        await self.temperatures(ctx)

    async def temperatures(self, ctx):
        # Trailing space is required for matching
        # temperatures at the end of the message.
        author = ctx.author.mention
        channel = ctx.channel

        # Abort if no temperature statement was found.
        statement = self.parse_request(ctx)
        if not statement:
            return

        # Check if input is ridiculous.
        if abs(statement["temperature"]) >= 10000:
            hotcold = "a bit chilly"

            if statement["temperature"] > 0:
                hotcold = "quite warm"

            await channel.send(
                    f"{author} No matter what unit you put that " +
                    f"in the answer is still gonna be \"{hotcold}\".")
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

        elif statement["origin"] == TempUnit.R:
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

        # Origin is "degrees", turning it into a real unit.
        elif statement[5]:
            if ctx.guild is not None:
                # Not DMs
                roles = ctx.author.roles
                if discord.utils.get(roles, name="Celsius") is not None:
                    result["origin"] = TempUnit.C
                elif discord.utils.get(roles, name="Fahrenheit") is not None:
                    result["origin"] = TempUnit.F
                elif discord.utils.get(roles, name="Canada") is not None:
                    result["origin"] = TempUnit.C
                elif discord.utils.get(roles, name="Mexico") is not None:
                    result["origin"] = TempUnit.C
                elif discord.utils.get(roles, name="North America") is not None:
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
            elif conversion[3]:
                result["destination"] = TempUnit.R
        else:
            result['manual'] = False
            if result["origin"] == TempUnit.F:
                result["destination"] = TempUnit.C
            elif result["origin"] == TempUnit.K:
                result["destination"] = TempUnit.C
            elif result["origin"] == TempUnit.C:
                result["destination"] = TempUnit.F
            elif result["origin"] == TempUnit.R:
                result["destination"] = TempUnit.F

            if TEMP_DEBUG:
                print(statement)
                print(f"{result['temperature']} {result['origin']} to " +
                      f"{result['destination']}. Manual: {result['manual']}")

        return result

    def celsius_table(self, temp, dest):
        if dest == TempUnit.C:
            return temp
        elif dest == TempUnit.F:
            return temp * 9.0 / 5.0 + 32
        elif dest == TempUnit.K:
            return temp + 273.15
        elif dest == TempUnit.R:
            return (temp + 273.15) * 9.0 / 5.0

    def fahrenheit_table(self, temp, dest):
        if dest == TempUnit.C:
            return (temp - 32) * 5.0 / 9.0
        elif dest == TempUnit.F:
            return temp
        elif dest == TempUnit.K:
            return (temp + 459.67) * 5.0 / 9.0
        elif dest == TempUnit.R:
            return temp + 459.67

    def kelvin_table(self, temp, dest):
        in_celsius = (temp - 273.15)
        return self.celsius_table(in_celsius, dest)

    def rankine_table(self, temp, dest):
        in_fahrenheit = (temp - 459.67)
        return self.fahrenheit_table(in_fahrenheit, dest)
