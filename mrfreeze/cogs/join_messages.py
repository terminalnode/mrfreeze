"""Cog for logging when users joins server."""
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
from mrfreeze.lib import welcome_messages


def setup(bot: MrFreeze) -> None:
    """Add the cog to the bot."""
    bot.add_cog(JoinMessages(bot))


class JoinMessages(Cog):
    """Manages how the bot acts when a member leaves a server."""

    def __init__(self, bot: MrFreeze) -> None:
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

        def_welcome = "Welcome to **$server**, $member!\n"
        def_welcome += "Please specify your region using `!region <region name>` "
        def_welcome += "to get a snazzy color for your nickname.\nThe available "
        def_welcome += "regions are: Asia, Europe, North America, South America, "
        def_welcome += "Africa, Oceania, Middle East and Antarctica."
        def_welcome += "\n\nDon't forget to read the $rules!"
        self.default_welcome_template = Template(def_welcome)

        self.coginfo = CogInfo(self)

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        """Log when a member joins the chat."""
        self.logger.info(f"{member} joined {member.guild}")
        if self.bot.listener_block_check(member):
            return

        welcome_channel = await welcome_messages.get_welcome_channel(member.guild, self.bot)
        msg = welcome_messages.welcome_member(member, self.coginfo)
        await welcome_channel.channel.send(msg)

    @commands.command(name="setwelcome", aliases=[ "setwelcomemessage", "setwelcomemsg" ])
    @commands.check(checks.is_owner_or_mod)
    async def set_welcome_message(self, ctx: Context) -> None:
        """Change the welcome message for the server."""
        msg = welcome_messages.set_message(ctx, self.bot)
        await ctx.send(msg)

    @commands.command(name="getwelcome", aliases=[ "getwelcomemessage", "getwelcomemsg" ])
    @commands.check(checks.is_owner_or_mod)
    async def get_welcome_message(self, ctx: Context) -> None:
        """Check what the current welcome message is."""
        msg = welcome_messages.get_message(ctx, self.bot, self.default_welcome_template)
        await ctx.send(msg)

    @commands.command(name="unsetwelcome", aliases=[ "delwelcome", "unwelcome" ])
    @commands.check(checks.is_owner_or_mod)
    async def unset_welcome(self, ctx: Context) -> None:
        """Change the welcome message for the server to use bot default."""
        msg = welcome_messages.unset_message(ctx, self.bot)
        await ctx.send(msg)

    @commands.command(name="simulatewelcome", aliases=[ "simwelcome", "testwelcome" ])
    @commands.check(checks.is_owner_or_mod)
    async def simulate_welcome_message(self, ctx: Context, *args: str) -> None:
        """Pretend that the caller of the command just joined the server."""
        text = " ".join(args)
        msg = welcome_messages.test_welcome_message(ctx.author, self.coginfo, text)
        await ctx.send(msg)

    @commands.command(name="getwelcomechannel", aliases=[ "getwelcomech", "getwelcomec" ])
    @commands.check(checks.is_owner_or_mod)
    async def get_leave_channel(self, ctx: Context) -> None:
        """Check what the current channel for welcome messages is."""
        msg = await welcome_messages.get_channel(ctx, self.coginfo)
        await ctx.send(msg)

    @commands.command(name="setwelcomechannel", aliases=[ "setwelcomech", "setwelcomec" ])
    @commands.check(checks.is_owner_or_mod)
    async def set_leave_channel(self, ctx: Context, channel: Optional[TextChannel]) -> None:
        """Set which channel to use for welcome messages (default is system channel)."""
        msg = await welcome_messages.set_channel(ctx, self.coginfo, channel)
        await ctx.send(msg)
