"""A module for handling editing and displaying of welcome messages."""

from string import Template

import discord
from discord import Member

from mrfreeze.bot import MrFreeze
from mrfreeze.lib import default


def get_message(member: Member, bot: MrFreeze, default_template: Template) -> str:
    """Log when a member joins the chat."""
    server = member.guild
    template_string = bot.settings.get_welcome_message(server)
    template = Template(template_string) if template_string else default_template

    rules_channel = discord.utils.get(member.guild.channels, name="rules")
    rules_channel = rules_channel.mention if rules_channel else "rules channel"

    return default.context_replacements(member, template, rules=rules_channel)
