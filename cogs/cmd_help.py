import discord
from discord.ext import commands

class UserCmdsCog():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', aliases=['halp', 'plzhelp', 'plshelp', 'plzhalp', 'plshalp', 'plz', 'pls'])
    async def _help(self, ctx):
        await ctx.send('%s Help is on the way!' % (ctx.author.mention,))


def setup(bot):
    bot.add_cog(UserCmdsCog(bot))
