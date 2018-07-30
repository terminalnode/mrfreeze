import discord
import botfunctions.native
from discord.ext import commands

class MrFreezeCog():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mrfreeze')
    async def _mrfreeze(self, ctx):
        quote = botfunctions.native.mrfreeze()
        quote = quote.replace('Batman', ctx.author.mention)
        quote = quote.replace('Gotham', '**' + ctx.guild.name + '**')
        await ctx.send(quote)

def setup(bot):
    bot.add_cog(MrFreezeCog(bot))
