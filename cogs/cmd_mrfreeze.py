import discord
import botfunctions.native
from discord.ext import commands

class MrFreezeCog():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mrfreeze')
    async def _mrfreeze(self, ctx, *args):
        # If they say the bot sucks, we'll default to the suck_reply.
        you_suck = ('sucks', 'suck', 'blows', 'blow')
        suck_reply = False
        for i in args:
            if i in you_suck:
                suck_reply = True

        # If they're asking for help, we'll default to the help_reply.
        pls_help = ('help', 'wtf', 'what', 'what\'s')
        help_reply = False
        for i in args:
            if i in pls_help:
                help_reply = True

        if help_reply:
            await ctx.send(ctx.author.mention + ' ' +
            'The command **!mrfreeze** will have me output one of my timeless quotes from Batman & Robin.')
        elif suck_reply:
            await ctx.send(ctx.author.mention + ' ' +
            'I suck? Well you\'re a smud!!')
        else:
            quote = botfunctions.native.mrfreeze()
            quote = quote.replace('Batman', ctx.author.mention)
            quote = quote.replace('Gotham', '**' + ctx.guild.name + '**')
            await ctx.send(quote)

def setup(bot):
    bot.add_cog(MrFreezeCog(bot))
