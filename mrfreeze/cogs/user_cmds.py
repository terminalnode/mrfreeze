"""Cog used for fun user commands."""

import random

import discord
from discord.ext.commands import BotMissingPermissions
from discord.ext.commands import bot_has_permissions
from discord.ext.commands import command
from discord.ext.commands.bot import Bot
from discord.ext.commands.bot import Context

from mrfreeze.cogs.cogbase import CogBase
from mrfreeze.lib import activity
from mrfreeze.lib import vote


def setup(bot: Bot) -> None:
    """Add the cog to the bot."""
    bot.add_cog(UserCommands(bot))


class UserCommands(CogBase):
    """
    These are the fun commands, everything else is boring and lame.

    Frankly there's no reason you should pay attention to anything that's not on this page.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(name="vote", aliases=["poll"])
    @bot_has_permissions(add_reactions=True)
    async def vote_cmd(self, ctx: Context, *args: str) -> None:
        """Create a poll."""
        await vote.vote(ctx, self.bot)

    @vote_cmd.error
    async def vote_cmd_error(self, ctx: Context, error: Exception) -> None:
        """Handle errors that happen in the vote command."""
        if isinstance(error, BotMissingPermissions):
            msg = f"{ctx.author.mention} The moderators goofed up it seems. "
            msg += "I'm not allowed to react."
            await ctx.send(msg)

    @command(name="praise")
    async def _praise(self, ctx: Context, *args: str) -> None:
        """Praise me."""
        author = ctx.author.mention
        msg = f"{author} Your praises have been heard, and "
        msg += "in return I bestow upon you... nothing!"
        await ctx.send(msg)

    @command(name="icon", aliases=["logo"])
    async def _logo(self, ctx: Context, *args: str) -> None:
        """Post the logo of the current server."""
        author = ctx.author.mention
        server = ctx.guild.name
        word = ctx.invoked_with

        logo = discord.Embed()
        logo.set_image(
            url=ctx.guild.icon_url_as(format="png")
        )
        await ctx.send(
            f"{author} Here's the server {word} for {server}!",
            embed=logo)

    @command(name="mrfreeze", aliases=["freeze"])
    async def _mrfreeze(self, ctx: Context, *args: str) -> None:
        """Get a quote from my timeless classic "Batman & Robin"."""
        author = ctx.author.mention
        server = ctx.guild.name

        with open("config/mrfreezequotes", "r") as f:
            quote = random.choice(f.read().strip().split('\n'))

        quote = quote.replace("Batman", author)
        quote = quote.replace("Gotham", f"**{server}**")
        await ctx.send(quote)

    @command(name="cointoss", aliases=["coin", "coinflip"])
    async def _cointoss(self, ctx: Context, *args: str) -> None:
        """Toss a coin, results are 50/50."""
        if random.randint(0, 1):
            await ctx.send(f"{ctx.author.mention} Heads")
        else:
            await ctx.send(f"{ctx.author.mention} Tails")

    @command(name="activity", aliases=[
        "listen", "listening", "playing", "play", "game", "gaming", "gameing",
        "stream", "streaming", "watch", "watching"])
    # @discord.ext.commands.cooldown(1, (60*10), BucketType.default)
    async def _activity(self, ctx: Context, *args: str) -> None:
        """Dictate what text should be displayed under my nick."""
        await activity.set_activity(ctx, self.bot, args)
