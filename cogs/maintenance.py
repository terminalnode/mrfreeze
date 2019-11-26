import discord                      # Basic discord functionality
# Required for bot restart
import sys
import os
# Required to run shell commands
from subprocess import run, PIPE
# Required to check that only bot owner can run commands
from internals import checks
from internals.cogbase import CogBase

# Some imports used in type hints
from discord.ext.commands.context import Context
from internals.mrfreeze import MrFreeze
from typing import Tuple


# This cog is for commands restricted to the owner of the bot (me!).
# It has features like !restart and !gitupdate.
def setup(bot):
    bot.add_cog(Maintenance(bot))


class Maintenance(CogBase):
    """
    There is only one person who is allowed to execute these commands...
    and it's probably not you.
    """
    def __init__(self, bot: MrFreeze):
        self.bot = bot

    @discord.ext.commands.command(name="restart")
    @discord.ext.commands.check(checks.is_owner)
    async def _restart(self, ctx: Context, *args: Tuple[str]) -> None:
        """
        Makes me restart if and only if you're Terminal.
        """
        mention: str = ctx.author.mention
        await ctx.send(f"{mention} Yes Dear Leader... I will restart now.")
        print("\n")  # extra new line after bot was restarted
        os.execl(sys.executable, sys.executable, *sys.argv)

    @discord.ext.commands.command(name="update")
    @discord.ext.commands.check(checks.is_owner)
    async def _gitupdate(self, ctx: Context, *args: Tuple[str]) -> None:
        """
        Makes me update myself if and only if you're TerminalNode.
        """
        # git fetch returns nothing if no updates were found
        # for some reason the output of git fetch is posted to stderr
        gitfetch: str = str(
            run(["git", "fetch"], stderr=PIPE, encoding="utf_8").stderr
        )
        gitpull: str = str(
            run(["git", "pull"], stdout=PIPE, encoding="utf_8").stdout
        )

        if gitfetch == "":
            gitfetch = "No output."

        # git seems to like to change how this message is written.
        do_restart: bool = False
        if "alreadyuptodate" not in gitpull.lower().replace("-", "").replace(" ", ""):
            do_restart = True

        output: str = (f"**git fetch:**\n{gitfetch}\n\n" +
                       f"**git pull:**\n{gitpull}")

        # If an update was found, restart automatically.
        await ctx.author.send(output)
        if do_restart:
            await ctx.send("Updates retrieved, restarting.")
            os.execl(sys.executable, sys.executable, *sys.argv)
