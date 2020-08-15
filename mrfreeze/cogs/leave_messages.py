"""Cog for logging when users leaves a server."""
import logging
from string import Template
from typing import Optional

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

        leave_channel = await leave_messages.get_leave_channel(member.guild, self.bot)
        embed = leave_messages.say_goodbye(member, self.coginfo)
        await leave_channel.channel.send(embed=embed)

    @commands.command(name="setleave", aliases=[ "setleavemessage", "setleavemsg" ])
    @commands.check(checks.is_owner_or_mod)
    async def set_leave_message(self, ctx: Context) -> None:
        """Change the leave message for the server."""
        msg = leave_messages.set_message(ctx, self.bot)
        await ctx.send(msg)

    @commands.command(name="getleave", aliases=[ "getleavemessage", "getleavemsg" ])
    @commands.check(checks.is_owner_or_mod)
    async def get_leave_message(self, ctx: Context) -> None:
        """Check what the current leave message is."""
        msg = leave_messages.get_message(ctx, self.bot, self.default_goodbye_template)
        await ctx.send(msg)

    @commands.command(name="unsetleave", aliases=[ "delleave", "unleave" ])
    @commands.check(checks.is_owner_or_mod)
    async def unset_leave(self, ctx: Context) -> None:
        """Change the leave message for the server to use bot default."""
        msg = leave_messages.unset_message(ctx, self.bot)
        await ctx.send(msg)

    @commands.command(name="simulateleave", aliases=[ "simleave", "testleave" ])
    @commands.check(checks.is_owner_or_mod)
    async def simulate_leave_message(self, ctx: Context, *args: str) -> None:
        """Pretend that the caller of the command just joined the server."""
        text = " ".join(args)
        leave_embed = leave_messages.test_leave_message(ctx.author, self.coginfo, text)
        await ctx.send(embed=leave_embed)

    @commands.command(name="getleavechannel", aliases=[ "getleavech", "getleavec" ])
    @commands.check(checks.is_owner_or_mod)
    async def get_leave_channel(self, ctx: Context) -> None:
        """Check what the current channel for leave messages is."""
        msg = await leave_messages.get_channel(ctx, self.coginfo)
        await ctx.send(msg)

    @commands.command(name="setleavechannel", aliases=[ "setleavech", "setleavec" ])
    @commands.check(checks.is_owner_or_mod)
    async def set_leave_channel(self, ctx: Context, channel: Optional[TextChannel]) -> None:
        """Set which channel to use for leave messages (default is system channel or trash channel)."""
        msg = await leave_messages.set_channel(ctx, self.coginfo, channel)
        await ctx.send(msg)
