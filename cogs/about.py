import discord
from discord.ext import commands
from internals import native

# Useful links for testing out embeds:
# https://leovoel.github.io/embed-visualizer/
# https://cog-creators.github.io/discord-embed-sandbox/

class AboutCog(commands.Cog, name='About'):
    """Use these commands to unlock my deepest, darkest inner secrets!"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='readme')
    async def _readme(self, ctx):
        """Hands you a link to the readme file over on Gitlab."""
        readme = discord.Embed(color=0x00dee9)
        readme.set_thumbnail(url=native.get_image('ReadMe'))
        readme.add_field(name = 'Readme',
                         value = ('There may be more information here than you\'re looking for, ' +
                                 'but my readme-file is available [here on Gitlab](https://gitlab.com/terminalnode/MrFreeze/blob/master/README.md)'))
        await ctx.send(embed=readme)


    @commands.command(name='source', aliases=['github', 'gitlab', 'git'])
    async def _source(self, ctx):
        """Hands you a link to the MrFreeze repository over on Gitlab."""
        source = discord.Embed(color=0x00dee9)
        source.set_thumbnail(url=native.get_image('Source'))
        source.add_field(name='Source code',
                         value='My source code is available on ' +
                               '[Gitlab](https://gitlab.com/terminalnode/MrFreeze/)!')
        await ctx.send(embed=source)

    @commands.command(name='getfreeze', aliases=['getfrozen', 'getmrfreeze', 'freezemeup', 'freezeme'])
    async def _getfreeze(self,ctx):
        """Get an invite link to invite MrFreeze to your server!"""
        mrfreeze = discord.Embed(color=0x00dee9,
                                description = (f"Here's a link for inviting me, **{self.bot.user.name}**, to a server." +
                                               f"The link will invite *this* version of me, be it the beta or regular version. Not the impostor.\n\n" +
                                               f"Note that **!banish** and **!region** won't function properly without the right infrastructure.")
            )
        mrfreeze.add_field(name=f"Invite link for {self.bot.user.name}",
                          value=(f"[Invite {self.bot.user.name} to a server.](https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot)")
            )
        await ctx.send(embed=mrfreeze)

    @commands.command(name='dummies')
    async def _dummies(self, ctx):
        """Supplies you with links to invite Ba'athman and Robin."""
        dummies = discord.Embed(color=0x00dee9,
                                description = ("Here are the links for inviting Ba'athman and Robin, my arch enemies, to a server.\n\n" +
                                               "They don't do anything at all, but are very useful for testing kick and ban commands."))
        dummies.set_thumbnail(url=native.get_image('Dummies'))
        dummies.add_field(name='Dummy Bots',
                          value=("[Invite Ba'athman to a server.](https://discordapp.com/oauth2/authorize?client_id=469030362119667712&scope=bot)\n" +
                                 "[Invite Robin to a server.](https://discordapp.com/oauth2/authorize?client_id=469030900492009472&scope=bot)"))

        await ctx.send(embed=dummies)

    @commands.command(name='todo', aliases=['TODO', 'TODOs', 'ToDo', 'ToDos', 'todos', 'whatsnext', 'whatnext'])
    async def _todos(self, ctx):
        """Supplies you with a list of my planned features."""
        todos = discord.Embed(color=0x00dee9)
        todos.set_thumbnail(url=native.get_image('TODOs'))
        todos.add_field(name="You're a nosy one! Here's a list of all the 'cool' stuff Terminal's got planned for me... :sleeping:",
                        value="https://gitlab.com/terminalnode/MrFreeze/blob/master/TODO.md")

        await ctx.send(embed=todos)

def setup(bot):
    bot.add_cog(AboutCog(bot))
