"""A module for handling editing and displaying of leave messages."""

from string import Template
from typing import Optional

from discord import Embed
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


def say_goodbye(member: Member, coginfo: CogInfo) -> Embed:
    """Log when a member leaves the server."""
    if coginfo.bot and coginfo.default_goodbye_template:
        bot: MrFreeze = coginfo.bot
        default_template: Template = coginfo.default_goodbye_template
    else:
        raise InsufficientCogInfo()

    template_string = bot.settings.get_leave_message(member.guild)
    template = Template(template_string) if template_string else default_template
    return create_embed(member, template)


def create_embed(member: Member, template: Template) -> Embed:
    """Fill out the data in a given template."""
    member_count_after = len(member.guild.members)
    member_count_before = member_count_after + 1

    text = default.context_replacements(
        member,
        template,
        member_count_after=member_count_after,
        member_count_before=member_count_before
    )

    embed = Embed(color=0x00dee9)
    embed.add_field(name="Member left", value=text)
    embed.set_thumbnail(url=member.avatar_url_as(static_format="png"))
    return embed


def test_leave_message(member: Member, coginfo: CogInfo, text: Optional[str]) -> Embed:
    """
    Simulate a leave message.

    If a string to test with is provided, use that, otherwise use the
    server's ordinary leave message.
    """
    if text:
        return create_embed(member, Template(text))
    else:
        return say_goodbye(member, coginfo)


def get_message(ctx: Context, bot: MrFreeze, default_template: Template) -> str:
    """Get the server's current leave message."""
    msg = bot.settings.get_leave_message(ctx.guild) or default_template.template

    return f"{ctx.author.mention} The welcome message for this server is:\n{msg}"


def set_message(ctx: Context, bot: MrFreeze) -> str:
    """Set the server's leave message."""
    new_msg = default.command_free_content(ctx)
    was_set = bot.settings.set_leave_message_by_id(ctx.guild, new_msg)

    if was_set:
        return f"{ctx.author.mention} The leave message has been set to:\n{new_msg}"
    else:
        return f"{ctx.author.mention} Something went awry, I couldn't change your leave message."


def unset_message(ctx: Context, bot: MrFreeze) -> str:
    """Unset the server's leave message, reverting to the default."""
    was_unset = bot.settings.set_leave_message_by_id(ctx.guild, None)

    if was_unset:
        return f"{ctx.author.mention} The leave message has been reset to bot default. :ok_hand:"
    else:
        return f"{ctx.author.mention} Something went awry, I couldn't unset your leave message."


async def get_leave_channel(guild: Guild, bot: MrFreeze) -> TypedChannel:
    """Get a LeaveChannel object representing which channel leave messages get posted in."""
    # Fetch leave channel, if there is any.
    db_leave = bot.settings.get_leave_channel(guild)
    leave_channel: Optional[TextChannel] = None
    if db_leave:
        try:
            leave_channel = await bot.fetch_channel(db_leave)
        except Exception:
            pass

    # Fetch trash channel, if there is no leave.
    db_trash = bot.settings.get_trash_channel(guild)
    trash_channel: Optional[TextChannel] = None
    if db_trash and not leave_channel:
        try:
            trash_channel = await bot.fetch_channel(db_trash)
        except Exception:
            pass

    # Return the appropriate channel
    if leave_channel:
        return TypedChannel(leave_channel, ChannelReturnType.LEAVE, ChannelReturnType.LEAVE)

    elif trash_channel:
        return TypedChannel(trash_channel, ChannelReturnType.TRASH, ChannelReturnType.LEAVE)

    else:
        sysmsg = guild.system_channel
        return TypedChannel(sysmsg, ChannelReturnType.SYSMSG, ChannelReturnType.LEAVE)


async def get_channel(ctx: Context, coginfo: CogInfo) -> str:
    """Get which channel is currently used for leave messages."""
    if coginfo.bot:
        bot: MrFreeze = coginfo.bot
    else:
        raise InsufficientCogInfo()

    channel = await get_leave_channel(ctx.guild, bot)
    return f"{ctx.author.mention} The current channel for leave messages is {channel}"


async def set_channel(ctx: Context, coginfo: CogInfo, channel: Optional[TextChannel]) -> str:
    """Set which channel should be used for leave messages."""
    if coginfo.bot:
        bot: MrFreeze = coginfo.bot
    else:
        raise InsufficientCogInfo()

    # Get old channel, do early return if the channels are the same.
    old_channel = await get_leave_channel(ctx.guild, bot)
    if old_channel.channel == channel and old_channel.type == ChannelReturnType.LEAVE:
        return f"{ctx.author.mention} The leave messages are already being posted to {old_channel}"

    # Try to change the channel, give responses accordingly
    new_value = channel.id if channel else channel
    channel_set = bot.settings.set_leave_channel_by_id(ctx.guild, new_value)

    if not channel_set:
        return f"{ctx.author.mention} Sorry, something went wrong when setting the leave messages channel."

    else:
        new_channel = await get_leave_channel(ctx.guild, bot)
        msg = f"{ctx.author.mention} Great success! Leave messages will no longer be posted to {old_channel}, "
        msg += f"from now on they will be posted in {new_channel}"
        return f"{ctx.author.mention} Great success! Leave messages will now be posted to {new_channel}!"
