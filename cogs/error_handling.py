import discord, re, traceback
from discord.ext import commands
from botfunctions import errorhandling

# Small script listening to all incoming messages looking for
# mentions of inks. Based on The Inkcyclopedia by klundtasaur:
# https://www.reddit.com/r/fountainpens/comments/5egjsa/klundtasaurs_inkcyclopedia_for_rfountainpens/

class ErrorHandlerCog(commands.Cog, name='ErrorHandler'):
    """How the bot acts when errors occur."""
    def __init__(self, bot):
        self.bot = bot
        self.inkydb = list()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        get_command = re.compile('!\w+')
        command = get_command.match(ctx.message.content).group()

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
