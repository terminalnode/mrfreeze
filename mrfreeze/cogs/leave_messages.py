"""Cog for logging when users leaves a server."""
import logging
from string import Template

import discord
from discord import Member
from discord import TextChannel
from discord.ext import commands
from discord.ext.commands import Cog
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.cogs.coginfo import CogInfo
from mrfreeze.lib import checks
from mrfreeze.lib import leave_messages


def setup(bot: MrFreeze) -> None:
    """Add the cog to the bot."""
    bot.add_cog(LeaveMessages(bot))


class LeaveMessages(Cog):
    """Manages how the bot acts when a member leaves a server."""

    def __init__(self, bot: MrFreeze) -> None:
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

        def_goodbye = "**$username** is a smudgerous trech who's turned their back on $server\n\n"
        def_goodbye += "We're now down to $member_count_after members. :sob:"
        self.default_goodbye_template = Template(def_goodbye)

        self.coginfo = CogInfo(self)

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        """Log when a member leaves the chat."""
        self.logger.info(f"{member} left {member.guild}")
        if self.bot.listener_block_check(member):
            return

        mod_channel: TextChannel = discord.utils.get(member.guild.text_channels, name="leaving-messages")
        embed = leave_messages.say_goodbye(member, self.coginfo)

        await mod_channel.send(embed=embed)

    @commands.command(name="simulateleave", aliases=[ "simleave", "testleave" ])
    @commands.check(checks.is_owner_or_mod)
    async def simulate_leave_message(self, ctx: Context, *args: str) -> None:
        """Pretend that the caller of the command just joined the server."""
        text = " ".join(args)
        leave_embed = leave_messages.test_leave_message(ctx.author, self.coginfo, text)
        await ctx.send(embed=leave_embed)
