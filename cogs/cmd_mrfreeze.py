import discord
import botfunctions.native
from discord.ext import commands

class MrFreezeCog():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mrfreeze')
    async def _mrfreeze(self, ctx, *args):
        you_suck = ('sucks', 'suck', 'blows', 'blow')

        suck_reply = False
        for i in args:
            if i in you_suck:
                suck_reply = True

        if suck_reply:
            await ctx.send(ctx.author.mention + ' No *you* suck!')
        else:
            quote = botfunctions.native.mrfreeze()
            quote = quote.replace('Batman', ctx.author.mention)
            quote = quote.replace('Gotham', '**' + ctx.guild.name + '**')
            await ctx.send(quote)

def setup(bot):
    bot.add_cog(MrFreezeCog(bot))
