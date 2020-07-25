"""Listener that detects and converts temperature statements."""

import re
from enum import Enum
from typing import Optional

import discord
from discord import Message
from discord.ext.commands import Cog
from discord.ext.commands import Context
from discord.ext.commands import command

from mrfreeze.bot import MrFreeze


class TempUnit(Enum):
    """Enumerator for the various temperature units."""

    C = "°C"
    K = "K"
    F = "°F"
    R = "°R"


class ParsedTemperature:
    """Class for holding the parsed temperature."""

    origin: TempUnit
    destination: TempUnit
    temperature: float
    in_c: float
    manual: bool

    def __init__(
        self,
        origin: TempUnit,
        destination: TempUnit,
        temperature: float,
        manual: bool
    ) -> None:
        self.origin = origin
        self.destination = destination
        self.temperature = temperature
        self.manual = manual
        self.in_c = self.convert(dest=TempUnit.C)

    def convert(self, dest: Optional[TempUnit] = None) -> float:
        """Convert from origin type to destination type."""
        origin = self.origin
        if origin == TempUnit.C or origin == TempUnit.K:
            return self.from_celsius(dest=dest)
        else:
            return self.from_fahrenheit(dest=dest)

    def from_celsius(self, dest: Optional[TempUnit] = None) -> float:
        """Convert from celsius to other units."""
        temperature = self.temperature
        if self.origin == TempUnit.K:
            temperature -= 273.15

        if dest is None:
            dest = self.destination

        if dest == TempUnit.C:
            return temperature
        elif dest == TempUnit.F:
            return temperature * 9.0 / 5.0 + 32
        elif dest == TempUnit.K:
            return temperature + 273.15
        else:  # Has to be rankine
            return (temperature + 273.15) * 9.0 / 5.0

    def from_fahrenheit(self, dest: Optional[TempUnit] = None) -> float:
        """Convert from fahrenheit to other units."""
        temperature = self.temperature
        if self.origin == TempUnit.R:
            temperature -= 459.67

        if dest is None:
            dest = self.destination

        if dest == TempUnit.C:
            return (temperature - 32) * 5.0 / 9.0
        elif dest == TempUnit.F:
            return temperature
        elif dest == TempUnit.K:
            return (temperature + 459.67) * 5.0 / 9.0
        else:  # Has to be rankine
            return temperature + 459.67


# Space or ° mandatory for kelvin to avoid
# collision with k as in thousand.
numbers = r"(?:^|\s)-?(?:[1-9]\d+|\d)(?:[,.]\d+)? ?"
celsius = r"°?(?:c|cel|celcius|celsius|civili[sz]ed units?)"
fahrenheit = r"°?(?:fah|fahrenheit|freedom units?)"
kelvin = r"(?:k|kelvin)"
rankine = r"°?(?:r|rankine)"
statement_regex = f"({numbers})(?:({celsius})|({fahrenheit})"
statement_regex += fr"|([ °]{kelvin})|({rankine}))(?:\s|$)"

# Regex for finding forced conversions
force_convert_begin = fr"(?:(?:{numbers}) ?(?:{celsius}|{fahrenheit}|"
force_convert_begin += fr"[ °]{kelvin}|{rankine})) (?:for|in|as"
force_convert_begin += r"|(?:convert )?to|convert)"
find_force_convert = fr"{force_convert_begin} (?:({celsius})|({fahrenheit})"
find_force_convert += fr"|(°?{kelvin})|({rankine}))(?:\s|$)"


def setup(bot: MrFreeze) -> None:
    """Add the cog to the bot."""
    bot.add_cog(TemperatureConverter(bot))


class TemperatureConverter(Cog):
    """Listener that detects and converts temperature statements."""

    def __init__(self, bot: MrFreeze) -> None:
        """Initialize the cog."""
        self.bot = bot

    async def is_number_within_range(self, msg: Message, statement: ParsedTemperature) -> bool:
        """
        Check if temperature is within acceptable limits.

        Return True if it is, return False and send a reply if not.
        """
        if abs(statement.temperature) >= 100000:
            hotcold = "a bit chilly"
            image_path = "images/hellacold.gif"

            if statement.temperature > 0:
                hotcold = "quite warm"
                image_path = "images/helldog.gif"

            reply = f"{msg.author.mention} That's {hotcold}."
            await msg.channel.send(reply, file=discord.File(image_path))
            return False

        return True

    def get_mute_status(self, ctx: Context, is_muted: bool) -> str:
        """Check if tempconverter is enabled for this server."""
        invocation = ctx.invoked_with

        if is_muted:
            msg = f"{ctx.author.mention} The {invocation} feature has been "
            msg += "**deactivated** for this server."
        else:
            msg = f"{ctx.author.mention} The {invocation} feature is "
            msg += "**active** for this server."

        return msg

    def get_changed_status(self, ctx: Context, before: bool, after: bool, want: bool) -> str:
        """Print a message saying if the tempconverter has been activated or deactivated."""
        mention = ctx.author.mention
        invocation = ctx.invoked_with

        if before == want:
            if want:
                return f"{mention} The {invocation} is already deactivated."
            else:
                return f"{mention} The {invocation} is already active."

        elif after != want:
            msg = f"{mention} Something went wrong, I wasn't able to "
            if want:
                return msg + "deactivate the {invocation}."
            else:
                return msg + "activate the {invocation}."

        else:
            if after:
                return f"{mention} The {invocation} is now deactivated."
            else:
                return f"{mention} The {invocation} is now activated."

    @command(name="tempconverter", aliases=[ "tempconversion", "temperatureconverter" ])
    async def tempconverter_command(self, ctx: Context, *args: str) -> None:
        """Check or change temperature converter mute status."""
        is_owner = await ctx.bot.is_owner(ctx.author)
        is_mod = ctx.author.guild_permissions.administrator
        is_muted = bool(self.bot.settings.is_tempconverter_muted(ctx.guild))
        owner_or_mod = is_owner or is_mod
        msg: Optional[str] = None

        if len(args) == 0 or not owner_or_mod:
            msg = self.get_mute_status(ctx, is_muted)

        elif args[0].lower() == "on":
            if is_muted:
                self.bot.settings.toggle_tempconverter_mute(ctx.guild)
                is_muted_after = bool(self.bot.settings.is_tempconverter_muted(ctx.guild))
                msg = self.get_changed_status(ctx, is_muted, is_muted_after, False)
            else:
                msg = self.get_changed_status(ctx, is_muted, is_muted, False)

        elif args[0].lower() == "off":
            if is_muted:
                msg = self.get_changed_status(ctx, is_muted, is_muted, True)
            else:
                self.bot.settings.toggle_tempconverter_mute(ctx.guild)
                is_muted_after = bool(self.bot.settings.is_tempconverter_muted(ctx.guild))
                msg = self.get_changed_status(ctx, is_muted, is_muted_after, True)

        elif args[0].lower() == "toggle":
            self.bot.settings.toggle_tempconverter_mute(ctx.guild)
            is_muted_after = bool(self.bot.settings.is_tempconverter_muted(ctx.guild))
            msg = self.get_changed_status(ctx, is_muted, is_muted_after, not is_muted)

        else:
            msg = self.get_mute_status(ctx, is_muted)

        if msg:
            await ctx.send(msg)

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        """Look through all messages received for temperature statements."""
        if message.author.bot or self.bot.listener_block_check(message):
            return

        if message.guild and self.bot.settings.is_tempconverter_muted(message.guild):
            return

        ctx = await self.bot.get_context(message)
        author = ctx.author.mention
        channel = ctx.channel

        # Abort if no temperature statement was found.
        parsed = self.parse_request(ctx)
        if not parsed:
            return

        # Check if input is ridiculously high/low.
        if not await self.is_number_within_range(message, parsed):
            return

        old_temp = round(parsed.temperature, 2)
        new_temp = round(parsed.convert(), 2)

        # hot/cold thresholds are defined in celsius
        image = None
        if parsed.in_c >= 35:
            image = discord.File("images/helldog.gif")
        elif parsed.in_c <= -20:
            image = discord.File("images/hellacold.gif")

        # old/new_temp contains the temperature values as floats.
        old_temp = round(parsed.temperature, 2)
        new_temp = round(new_temp, 2)
        # Check if old and new temp are the same temperatures or units.
        no_change = (old_temp == new_temp)
        same_unit = (parsed.origin == parsed.destination)
        # Get the abbreviations for each temperature unit
        origin = parsed.origin.value
        destination = parsed.destination.value

        # Time for the reply.
        if no_change:
            if same_unit and parsed.manual:
                reply = f"Did {author} just try to convert {old_temp}"
                reply += f"{origin} to {destination}? :thinking:"
            elif parsed.manual:
                reply = f"Uh... {old_temp}{origin} is the same in "
                reply += f"{new_temp}{destination} you smud. :angry:"
            else:
                reply = f"Guess what! {old_temp}{origin} is the same as "
                reply += f"{new_temp}{destination}! WOOOW!"
        else:
            reply = f"{old_temp}{origin} is around {new_temp}{destination}"
        await channel.send(reply, file=image)

    def parse_request(self, ctx: Context) -> Optional[ParsedTemperature]:
        """
        Extract temperature statement from text.

        If no temperature statement is found returns false.
        Otherwise returns a dictionary with keys:
            temperature, origin, destination, manual
        """
        origin: TempUnit
        destination: TempUnit
        temperature: float
        is_manual: bool

        text = ctx.message.content
        statement_match = re.search(statement_regex, text, re.IGNORECASE)
        if not statement_match:
            return None
        conversion_match = re.search(find_force_convert, text, re.IGNORECASE)

        # Determine the origin unit.
        statement = statement_match.groups()
        temperature = float(statement[0].replace(",", "."))

        if statement[1]:
            origin = TempUnit.C
        elif statement[2]:
            origin = TempUnit.F
        elif statement[3]:
            origin = TempUnit.K
        else:  # Has to be rankine
            origin = TempUnit.R

        # Determine destination unit
        if conversion_match:
            is_manual = True
            conversion = conversion_match.groups()
            if conversion[0]:
                destination = TempUnit.C
            elif conversion[1]:
                destination = TempUnit.F
            elif conversion[2]:
                destination = TempUnit.K
            else:  # Has to be rankine
                destination = TempUnit.R
        else:
            is_manual = False
            if origin == TempUnit.F:
                destination = TempUnit.C
            elif origin == TempUnit.K:
                destination = TempUnit.C
            elif origin == TempUnit.C:
                destination = TempUnit.F
            else:  # Has to be rankine
                destination = TempUnit.F

        return ParsedTemperature(origin, destination, temperature, is_manual)
