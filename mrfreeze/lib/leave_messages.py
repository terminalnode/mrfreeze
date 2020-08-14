"""A module for handling editing and displaying of leave messages."""

from string import Template
from typing import Optional

from discord import Embed
from discord import Member
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.cogs.coginfo import CogInfo
from mrfreeze.cogs.coginfo import InsufficientCogInfo
from mrfreeze.lib import default


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
