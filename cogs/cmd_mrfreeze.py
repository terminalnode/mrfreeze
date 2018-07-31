import discord
import botfunctions.native
from discord.ext import commands

class MrFreezeCog():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mrfreeze', aliases=['freeze'])
    async def _mrfreeze(self, ctx, *args):
        # If they're asking for help, we'll default to the help_reply.
        pls_help = ('help', 'wtf', 'what', 'what\'s', 'wut', 'woot')
        help_reply = False
        for i in pls_help:
            if i in args:
                help_reply = True

        # If they say the bot sucks, we'll default to the suck_reply.
        you_suck = ('sucks', 'suck', 'blows', 'blow')
        suck_reply = False
        for i in you_suck:
            if i in args:
                suck_reply = True

        # If they're telling the bot to kill itself... well...
        death_reply = False
        passive_die = ('die', 'suicide')
        for i in args:
            if i in passive_die:
                death_reply = True

        active_die  = ('kill', 'murder', 'destroy')
        yourself_spells = ('yourself', 'urself', 'uself', 'u', 'you')
        for i in active_die:
            for k in yourself_spells:
                if i and k in args:
                    death_reply = True

        if help_reply:
            await ctx.send('Allow me to break the ice: My name is Freeze and ' +
            'the command **!mrfreeze** will have me print one of my timeless quotes from Batman & Robin.')
        elif suck_reply:
            await ctx.send('Freeze in hell,' + ctx.author.mention + '!')
        elif death_reply:
            await ctx.send(ctx.author.mention + ' ' +
            'You\'re not sending ME to the COOLER!')
        else:
            quote = botfunctions.native.mrfreeze()
            quote = quote.replace('Batman', ctx.author.mention)
            quote = quote.replace('Gotham', '**' + ctx.guild.name + '**')
            await ctx.send(quote)

def setup(bot):
    bot.add_cog(MrFreezeCog(bot))
