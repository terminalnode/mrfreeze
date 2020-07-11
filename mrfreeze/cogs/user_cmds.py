"""Cog used for fun user commands."""

import random
from typing import Optional

import discord
from discord.ext.commands import BotMissingPermissions
from discord.ext.commands import bot_has_permissions
from discord.ext.commands import command
from discord.ext.commands.bot import Bot
from discord.ext.commands.bot import Context

from mrfreeze.cogs.cogbase import CogBase
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
        # Dictionary of all different activity types with keywords.
        # The keywords are defined in separate tuples so I can access
        # them without the dictionary.
        play_words = ("play", "playing", "game", "gaming", "gameing")
        stream_words = ("stream", "streaming")
        listen_words = ("listen", "listening")
        watch_words = ("watch", "watching")

        activity_types = {
            None: ("activity",),
            discord.ActivityType.playing: play_words,
            discord.ActivityType.streaming: stream_words,
            discord.ActivityType.listening: listen_words,
            discord.ActivityType.watching: watch_words
        }

        # We will determine the chosen activity in one of two ways.
        # 1. By checking which alias they used.
        # 2. By seeing which arguments they tried.
        for type in activity_types:
            for alias in activity_types[type]:
                if alias == ctx.invoked_with:
                    chosen_activity = type

        # On to step 2, seeing which arguments they tried and
        # possibly identifying a type of activity.
        if chosen_activity is None:
            for activity in activity_types:
                for alias in activity_types[activity]:
                    without_is = len(args) >= 1 and (args[0] == alias)
                    with_is = (len(args) >= 2) and (args[0:2] == ("is", alias))
                    if without_is:
                        chosen_activity = activity
                        args = args[1:]

                    elif with_is:
                        chosen_activity = activity
                        args = args[2:]

        success = False
        max_activity_length = 30
        if len(args) != 0:
            joint_args = ' '.join(args)

            # If we haven't been able to identify an
            # activity we'll default to listening.
            if chosen_activity is None:
                chosen_activity = discord.ActivityType.listening

            if len(joint_args) <= max_activity_length:
                try:
                    activity_obj = discord.Activity(
                        name=joint_args,
                        type=chosen_activity)
                    await self.bot.change_presence(activity=activity_obj)
                    success = True
                except Exception:
                    pass

        if chosen_activity == discord.ActivityType.playing:
            reply_activity = "playing"
        elif chosen_activity == discord.ActivityType.streaming:
            # streaming doesn't work as I want it,
            # always says playing not streaming.
            reply_activity = "playing"
        elif chosen_activity == discord.ActivityType.listening:
            reply_activity = "listening to"
        elif chosen_activity == discord.ActivityType.watching:
            reply_activity = "watching"
        else:
            # Default activity.
            reply_activity = "listening to"

        msg: Optional[str] = None
        if success:
            msg = f"{ctx.author.mention} OK then, I guess I'm "
            msg += f"**{reply_activity} {joint_args}** now."

        elif len(args) == 0:
            # No activity specified.
            if chosen_activity is None:
                msg = f"{ctx.author.mention} You didn't tell me what to do."

            else:
                # No name specified.
                msg = f"{ctx.author.mention} I can tell you want me to be **{reply_activity}** "
                msg += "something, but I don't know what."

        elif len(joint_args) >= max_activity_length:
            # Too long.
            msg = f"{ctx.author.mention} That activity is stupidly long ({len(joint_args)}). "
            msg += f"The limit is {max_activity_length} characters."

        else:
            msg = "<@!154516898434908160> Something went wrong when trying to change my "
            msg += "activity and I have no idea what. Come see!"

        if msg:
            await ctx.send(msg)
