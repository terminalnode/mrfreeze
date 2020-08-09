"""Cog for logging when users join or leave a server."""
from string import Template
from typing import List

import discord
from discord import Embed
from discord import Member
from discord import TextChannel
from discord.ext import commands
from discord.ext.commands import Cog
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.lib import checks
from mrfreeze.lib import welcome_messages


def setup(bot: MrFreeze) -> None:
    """Add the cog to the bot."""
    bot.add_cog(DeparturesAndArrivals(bot))


class DeparturesAndArrivals(Cog):
    """Manages how the bot acts when a member leaves a server."""

    def __init__(self, bot: MrFreeze) -> None:
        self.bot = bot

        def_welcome = "Welcome to **$server**, $member!\n"
        def_welcome += "Please specify your region using `!region <region name>` "
        def_welcome += "to get a snazzy color for your nickname.\nThe available "
        def_welcome += "regions are: Asia, Europe, North America, South America, "
        def_welcome += "Africa, Oceania, Middle East and Antarctica."
        def_welcome += "\n\nDon't forget to read the $rules!"
        self.default_welcome = Template(def_welcome)

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        """Log when a member leaves the chat."""
        if self.bot.listener_block_check(member):
            return

        guild_channels: List[TextChannel] = member.guild.text_channels
        mod_channel: TextChannel = discord.utils.get(guild_channels, name="leaving-messages")
        mention: str = member.mention
        username: str = f"{member.name}#{member.discriminator}"

        embed = Embed(color=0x00dee9)
        embed.set_thumbnail(url=member.avatar_url_as(static_format="png"))

        embed_text = f"{mention} is a smudgerous trech who's turned their back on "
        embed_text += f"{member.guild.name}.\n\n"
        embed_text += f"We're now down to {len(member.guild.members)} members."
        embed.add_field(name=f"{username} has left the server! :sob:", value=embed_text)
        await mod_channel.send(embed=embed)

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        """Log when a member joins the chat."""
        if self.bot.listener_block_check(member):
            return

        msg = welcome_messages.welcome_member(member, self.bot, self.default_welcome)
        await member.guild.system_channel.send(msg)

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
        msg = welcome_messages.get_message(ctx, self.bot, self.default_welcome)
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
        author = ctx.author
        msg = welcome_messages.test_welcome_message(author, self.bot, text, self.default_welcome)
        await ctx.send(msg)
