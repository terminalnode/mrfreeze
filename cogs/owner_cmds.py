import discord, sys, os
from discord.ext import commands

class OwnerCmdsCog:
    def __init__(self, bot):
        self.bot = bot

    ####### restart #######
    ### RESTART THE Bot ###
    #######################
    @commands.command(name='restart')
    async def _restart(self, ctx, *kwargs):
        if ctx.author.id == 154516898434908160: # This is my discord user ID. If you're modifying this, change to your ID.
            await ctx.send(ctx.author.mention + " Yes Dear Leader... I will restart now.")
            print ('\n') # extra new line after the commandlog() output
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            await ctx.send(ctx.author.mention + " You're not the boss of me, I restart when Terminal wants me to.")

def setup(bot):
    bot.add_cog(OwnerCmdsCog(bot))
