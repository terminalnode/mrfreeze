"""A module for handling editing and displaying of welcome messages."""

from string import Template
from typing import Optional

import discord
from discord import Guild
from discord import Member
from discord import TextChannel
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.cogs.coginfo import CogInfo
from mrfreeze.cogs.coginfo import InsufficientCogInfo
from mrfreeze.lib import default
from mrfreeze.lib.channel_settings import ChannelReturnType
from mrfreeze.lib.channel_settings import TypedChannel


def welcome_member(member: Member, coginfo: CogInfo) -> str:
    """Log when a member joins the chat."""
    if coginfo.bot and coginfo.default_welcome_template:
        bot: MrFreeze = coginfo.bot
        default_template: Template = coginfo.default_welcome_template
    else:
        raise InsufficientCogInfo()

    template_string = bot.settings.get_welcome_message(member.guild)
    template = Template(template_string) if template_string else default_template
    return fill_template(member, template)


def fill_template(member: Member, template: Template) -> str:
    """Fill out the data in a given template."""
    rules_channel = discord.utils.get(member.guild.channels, name="rules")
    rules_channel = rules_channel.mention if rules_channel else "rules channel"
    return default.context_replacements(member, template, rules=rules_channel)


def test_welcome_message(member: Member, coginfo: CogInfo, text: Optional[str]) -> str:
    """
    Simulate a welcome message.

    If a string to test with is provided, use that, otherwise use the
    server's ordinary welcome message.
    """
    if text:
        return fill_template(member, Template(text))
    else:
        return welcome_member(member, coginfo)


def get_message(ctx: Context, bot: MrFreeze, default_template: Template) -> str:
    """Get the server's current welcome message."""
    msg = bot.settings.get_welcome_message(ctx.guild) or default_template.template

    return f"{ctx.author.mention} The welcome message for this server is:\n{msg}"


def set_message(ctx: Context, bot: MrFreeze) -> str:
    """Set the server's welcome message."""
    new_msg = default.command_free_content(ctx)
    was_set = bot.settings.set_welcome_message_by_id(ctx.guild, new_msg)

    if was_set:
        return f"{ctx.author.mention} The welcome message has been set to:\n{new_msg}"
    else:
        return f"{ctx.author.mention} Something went awry, I couldn't change your welcome message."


def unset_message(ctx: Context, bot: MrFreeze) -> str:
    """Unset the server's welcome message, reverting to the default."""
    was_unset = bot.settings.set_welcome_message_by_id(ctx.guild, None)

    if was_unset:
        return f"{ctx.author.mention} The welcome message has been reset to bot default. :ok_hand:"
    else:
        return f"{ctx.author.mention} Something went awry, I couldn't unset your welcome message."


async def get_welcome_channel(guild: Guild, bot: MrFreeze) -> TypedChannel:
    """Get a WelcomeChannel object representing which channel welcome messages get posted in."""
    # Fetch welcome channel, if there is any.
    db_welcome = bot.settings.get_welcome_channel(guild)
    welcome_channel: Optional[TextChannel] = None
    if db_welcome:
        try:
            welcome_channel = await bot.fetch_channel(db_welcome)
        except Exception:
            pass

    # Return the appropriate channel
    if welcome_channel:
        return TypedChannel(welcome_channel, ChannelReturnType.WELCOME, ChannelReturnType.WELCOME)

    else:
        sysmsg = guild.system_channel
        return TypedChannel(sysmsg, ChannelReturnType.SYSMSG, ChannelReturnType.WELCOME)


async def get_channel(ctx: Context, coginfo: CogInfo) -> str:
    """Get which channel is currently used for welcome messages."""
    if coginfo.bot:
        bot: MrFreeze = coginfo.bot
    else:
        raise InsufficientCogInfo()

    channel = await get_welcome_channel(ctx.guild, bot)
    return f"{ctx.author.mention} The current channel for welcome messages is {channel}"


async def set_channel(ctx: Context, coginfo: CogInfo, channel: Optional[TextChannel]) -> str:
    """Set which channel should be used for welcome messages."""
    if coginfo.bot:
        bot: MrFreeze = coginfo.bot
    else:
        raise InsufficientCogInfo()

    # Get old channel, do early return if the channels are the same.
    old_channel = await get_welcome_channel(ctx.guild, bot)
    if old_channel.channel == channel and old_channel.type == ChannelReturnType.WELCOME:
        return f"{ctx.author.mention} The welcome messages are already being posted to {old_channel}"

    # Try to change the channel, give responses accordingly
    new_value = channel.id if channel else channel
    channel_set = bot.settings.set_welcome_channel_by_id(ctx.guild, new_value)

    if not channel_set:
        return f"{ctx.author.mention} Sorry, something went wrong when setting the welcome messages channel."

    else:
        new_channel = await get_welcome_channel(ctx.guild, bot)
        msg = f"{ctx.author.mention} Great success! Welcome messages will no longer be posted to {old_channel}, "
        msg += f"from now on they will be posted in {new_channel}"
        return f"{ctx.author.mention} Great success! Welcome messages will now be posted to {new_channel}!"
