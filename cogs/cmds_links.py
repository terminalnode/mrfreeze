import discord
from discord.ext import commands

# This cog is meant for things like posting a link to github, posting a link to the readme etc.
# TODO: Make the links embedded: https://leovoel.github.io/embed-visualizer/

class BragCog():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='readme')
    async def _readme(self, ctx, *args):
        await ctx.send('This may be more information than you\'re looking for, ' +
                               'but here\'s a link to the readme for you:\n' +
                               '<https://github.com/kaminix/MrFreezeRW/blob/master/README.md>')

    @commands.command(name='source', aliases=['github'])
    async def _source(self, ctx, *args):
        source = discord.Embed(color=0x00dee9)
        source.set_thumbnail(url='https://i.imgur.com/sVP6w67.png')
        source.add_field(name='Source code',
                         value='My source code is available on ' +
                               '[Github](https://github.com/kaminix/MrFreezeRW)!')
        await ctx.send(embed=source)

    @commands.command(name='dummies')
    async def _dummies(self, ctx, *args):
        # Robin avatar URL:
        # https://cdn.discordapp.com/avatars/469030900492009472/5326bec1dc7aa3f20b0b1651070fc069.webp?size=1024
        # Ba'athman avatar URL:
        # https://cdn.discordapp.com/avatars/469030362119667712/7d6ecde5d7c0b85231102aa5b4286563.webp?size=1024

        dummies = discord.Embed(color=0x00dee9)
        dummies.set_thumbnail(url="https://i.imgur.com/r4MrUbX.png")
        dummies.add_field(name='Ba\'athman:',
                          value='[Invite Ba\'athman](https://discordapp.com/oauth2/authorize?client_id=469030362119667712&scope=bot)\n',
                          inline=False)
        dummies.add_field(name='Robin:',
                          value='[Invite Robin](https://discordapp.com/oauth2/authorize?client_id=469030900492009472&scope=bot)',
                          inline=False)

        await ctx.send('Here are the links for inviting Ba\'athman and Robin, my arch enemies, to a server:', embed=dummies)

def setup(bot):
    bot.add_cog(BragCog(bot))
