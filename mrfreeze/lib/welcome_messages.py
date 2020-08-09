"""A module for handling editing and displaying of welcome messages."""

from string import Template
from typing import Optional

import discord
from discord import Member
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.lib import default


def welcome_member(member: Member, bot: MrFreeze, default_template: Template) -> str:
    """Log when a member joins the chat."""
    template_string = bot.settings.get_welcome_message(member.guild)
    template = Template(template_string) if template_string else default_template
    return fill_template(member, template)


def fill_template(member: Member, template: Template) -> str:
    """Fill out the data in a given template."""
    rules_channel = discord.utils.get(member.guild.channels, name="rules")
    rules_channel = rules_channel.mention if rules_channel else "rules channel"
    return default.context_replacements(member, template, rules=rules_channel)


def test_welcome_message(
    member: Member,
    bot: MrFreeze,
    text: Optional[str],
    default_template: Template
) -> str:
    """
    Simulate a welcome message.

    If a string to test with is provided, use that, otherwise use the
    server's ordinary welcome message.
    """
    if text:
        return fill_template(member, Template(text))
    else:
        return welcome_member(member, bot, default_template)


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
