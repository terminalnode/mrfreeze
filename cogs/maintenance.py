import discord, sys, os
from subprocess import run, PIPE
from discord.ext import commands
from internals import checks

# This cog is for commands restricted to the owner of the bot (me!).
# It has features like !restart and !gitupdate.

class MaintenanceCog(commands.Cog, name='Maintenance'):
    """There is only one person who is allowed to execute these commands... and it's not you."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='restart')
    @commands.check(checks.is_owner)
    async def _restart(self, ctx, *args):
        """Makes me restart if and only if you're Terminal."""
        await ctx.send(ctx.author.mention + " Yes Dear Leader... I will restart now.")
        print ('\n') # extra new line after the commandlog() output
        os.execl(sys.executable, sys.executable, *sys.argv)

    @commands.command(name='update')
    @commands.check(checks.is_owner)
    async def _gitupdate(self, ctx, *args):
        """Makes me update myself if and only if you're Terminal."""
        # git fetch returns nothing if no updates were found
        # for some reason the output of git fetch is posted to stderr
        gitfetch = str(run(['git', 'fetch'], stderr=PIPE, encoding='utf_8').stderr)
        gitpull = str(run(['git', 'pull'], stdout=PIPE, encoding='utf_8').stdout)
        output = str()

        if gitfetch == '':
            gitfetch = 'No output.'

        if gitpull != 'Already up-to-date.':
            do_restart = True
        else:
            do_restart = False

        output += '**git fetch:**\n'
        output += gitfetch + '\n\n'
        output += '**git pull:**\n'
        output += gitpull

        await ctx.author.send(output)

        if do_restart:
            await ctx.send('Updates retrieved, restarting.')

        # If an update was found, restart automatically.
        if do_restart:
            os.execl(sys.executable, sys.executable, *sys.argv)

def setup(bot):
    bot.add_cog(MaintenanceCog(bot))
