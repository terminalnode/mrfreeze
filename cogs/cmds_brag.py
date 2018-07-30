import discord, re
from discord.ext import commands

# This cog is meant for things like posting a link to github, posting a link to the readme etc.
# TODO: Make the links embedded: https://leovoel.github.io/embed-visualizer/

class BragCog():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='readme')
    async def _readme(self, ctx, *args):
        await ctx.channel.send('This may be more information than you\'re looking for, ' +
                               'but here\'s a link to the readme for you:\n' +
                               '<https://github.com/kaminix/MrFreezeRW/blob/master/README.md>')

    @commands.command(name='source', aliases=['github'])
    async def _source(self, ctx, *args):
        await ctx.channel.send('My source code is available at:\n' +
                               'https://github.com/kaminix/MrFreezeRW')

    @commands.command(name='dummies')
    async def _dummies(self, ctx, *args):
        await ctx.channel.send('Ba\'athman: <https://discordapp.com/oauth2/authorize?client_id=469030362119667712&scope=bot>\n' +
                          'Robin: <https://discordapp.com/oauth2/authorize?client_id=469030900492009472&scope=bot>\n')

def setup(bot):
    bot.add_cog(BragCog(bot))
