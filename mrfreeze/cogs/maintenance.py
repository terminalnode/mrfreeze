"""Small cog with a few owner-commands used for bot maintenance."""

import os
import sys
from subprocess import PIPE
from subprocess import run
from typing import Tuple

import discord
from discord.ext.commands.context import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.cogs.cogbase import CogBase
from mrfreeze.lib import checks


# This cog is for commands restricted to the owner of the bot (me!).
# It has features like !restart and !gitupdate.
def setup(bot: MrFreeze) -> None:
    """Add the cog to the bot."""
    bot.add_cog(Maintenance(bot))


class Maintenance(CogBase):
    """Bot maintenance commands."""

    def __init__(self, bot: MrFreeze) -> None:
        self.bot = bot

    @discord.ext.commands.command(name="restart")
    @discord.ext.commands.check(checks.is_owner)
    async def _restart(self, ctx: Context, *args: Tuple[str]) -> None:
        """Make me restart if and only if you're TerminalNode."""
        mention: str = ctx.author.mention

        await ctx.send(f"{mention} Yes Dear Leader... I will restart now.")
        os.execl(sys.executable, sys.executable, *sys.argv)

    @discord.ext.commands.command(name="update")
    @discord.ext.commands.check(checks.is_owner)
    async def _gitupdate(self, ctx: Context, *args: Tuple[str]) -> None:
        """Make me update myself if and only if you're TerminalNode."""
        gitfetch: str
        gitpull: str
        output: str
        do_restart: bool = False

        # git fetch returns nothing if no updates were found
        # for some reason the output of git fetch is posted to stderr
        gitfetch = str(run(["git", "fetch"], stderr=PIPE, encoding="utf_8").stderr)
        gitpull = str(run(["git", "pull"], stdout=PIPE, encoding="utf_8").stdout)

        if gitfetch == "":
            gitfetch = "No output."

        # git seems to like to change how this message is written.
        sanitized_gitpull = gitpull.lower().replace("-", "").replace(" ", "")
        if "alreadyuptodate" not in sanitized_gitpull:
            do_restart = True

        output  = f"**git fetch:**\n{gitfetch}\n\n"
        output += f"**git pull:**\n{gitpull}"

        # If an update was found, restart automatically.
        await ctx.author.send(output)
        if do_restart:
            await ctx.send("Updates retrieved, restarting.")
            os.execl(sys.executable, sys.executable, *sys.argv)
