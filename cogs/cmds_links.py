import discord
from discord.ext import commands
from botfunctions import native

# Useful links for testing out embeds:
# https://leovoel.github.io/embed-visualizer/
# https://cog-creators.github.io/discord-embed-sandbox/

class BragCog():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='readme')
    async def _readme(self, ctx, *args):
        readme = discord.Embed(color=0x00dee9)
        readme.set_thumbnail(url=native.get_image('ReadMe'))
        readme.add_field(name = 'Readme',
                         value = ('There may be more information here than you\'re looking for, ' +
                                 'but my readme-file is available [here on Github](https://github.com/kaminix/MrFreezeRW/blob/master/README.md)'))
        await ctx.send(embed=readme)


    @commands.command(name='source', aliases=['github'])
    async def _source(self, ctx, *args):
        source = discord.Embed(color=0x00dee9)
        source.set_thumbnail(url=native.get_image('Source'))
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

        dummies = discord.Embed(color=0x00dee9,
                                description = ('Here are the links for inviting Ba\'athman and Robin, my arch enemies, to a server.\n\n' +
                                               'They don\'t do anything at all, but are very useful for testing kick and ban commands.'))
        dummies.set_thumbnail(url=native.get_image('Dummies'))
        dummies.add_field(name='Dummy Bots',
                          value=('[Invite Ba\'athman to a server.](https://discordapp.com/oauth2/authorize?client_id=469030362119667712&scope=bot)\n' +
                                 '[Invite Robin to a server.](https://discordapp.com/oauth2/authorize?client_id=469030900492009472&scope=bot)'))

        await ctx.send(embed=dummies)

def setup(bot):
    bot.add_cog(BragCog(bot))
