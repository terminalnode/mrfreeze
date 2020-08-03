"""
A cog for tools intended primarily for debugging and such.

Tools that do not affect operations can be run by administrators or bot owner,
other tools can only by run by the bot owner.
"""

import logging

import discord
from discord.ext import commands
from discord.ext.commands import Cog
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.lib.checks import is_owner_or_mod


def setup(bot: MrFreeze) -> None:
    """Add the cog to the bot."""
    bot.add_cog(DevTools(bot))


class DevTools(Cog):
    """Commands used for changing the log level of a component."""

    def __init__(self, bot: MrFreeze) -> None:
        """Initialize the DevTools cog."""
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    @commands.command(name="userid", aliases=["uid"])
    @commands.check(is_owner_or_mod)
    async def user_from_id(self, ctx: Context, uid: int) -> None:
        """Get a given user by ID."""
        msg = None
        try:
            user = await ctx.bot.fetch_user(uid)
            msg = f"{ctx.author.mention} That would be {user}."

        except discord.NotFound:
            msg = f"{ctx.author.mention} I don't know who that user is."

        except discord.HTTPException:
            msg = f"{ctx.author.mention} Sorry, Internet died. Come again?"

        if msg:
            await ctx.send(msg)

    @commands.command(name="guildid", aliases=["gid"])
    @commands.check(is_owner_or_mod)
    async def guild_from_id(self, ctx: Context, gid: int) -> None:
        """Get a given guild/server by ID."""
        msg = None
        try:
            guild = await ctx.bot.fetch_guild(gid)
            if guild == ctx.guild:
                msg = f"{ctx.author.mention} That would be **{guild}**, this one!"
            else:
                msg = f"{ctx.author.mention} That would be **{guild}**."

        except discord.Forbidden:
            msg = f"{ctx.author.mention} I don't have access to that guild."

        except discord.HTTPException:
            msg = f"{ctx.author.mention} Sorry, Internet died. Come again?"

        if msg:
            await ctx.send(msg)

    @commands.command(name="channelid", aliases=["chanid", "cid"])
    @commands.check(is_owner_or_mod)
    async def channel_from_id(self, ctx: Context, cid: int) -> None:
        """Get a given channel by ID."""
        msg = None
        try:
            channel = await ctx.bot.fetch_channel(cid)
            server = channel.guild
            if server == ctx.guild:
                msg = f"{ctx.author.mention} That would be {channel.mention}."
            else:
                msg = f"{ctx.author.mention} That would be **#{channel}** in **{server}**."

        except discord.NotFound:
            msg = f"{ctx.author.mention} I don't know what that channel is."

        except discord.Forbidden:
            msg = f"{ctx.author.mention} That's some kind of spooky secret channel."

        except discord.HTTPException:
            msg = f"{ctx.author.mention} Sorry, Internet died. Come again?"

        except discord.InvalidData:
            msg = f"{ctx.author.mention} Jesus christ, what is that thing? "
            msg += "Discord sent me something which can not be named."

        if msg:
            await ctx.send(msg)
