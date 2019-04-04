import discord, re, traceback, sys
from discord.ext import commands
from botfunctions import errorhandling

class ErrorHandlerCog(commands.Cog, name='ErrorHandler'):
    """How the bot acts when errors occur."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            errorhandling.checkfailure(ctx, error)

        elif isinstance(error, commands.errors.CommandOnCooldown):
            replystr = errorhandling.cooldown(ctx, error)
            await ctx.send(replystr)

        elif isinstance(error, discord.ext.commands.errors.BadArgument):
            await ctx.send(ctx.author.mention + ' That\'s not quite the information I need to execute that command.')

        else:
            print(error)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
    bot.add_cog(ErrorHandlerCog(bot))
