import discord # Basic discord functionality

def setup(bot):
    bot.add_cog(AboutCog(bot))
 
class AboutCog(discord.ext.commands.Cog, name='About'):
    """Use these commands to unlock my deepest, darkest inner secrets!"""
    def __init__(self, bot):
        self.bot = bot

    @discord.ext.commands.command(name='readme')
    async def _readme(self, ctx):
        """Hands you a link to the readme file over on Github."""
        url = "https://github.com/terminalnode/mrfreeze/blob/master/README.md"

        embed = discord.Embed(color=0x00dee9)
        embed.add_field(
            name = "Readme",
            value = f"My readme file is available [on Github]({url})")

        image = discord.File("images/readme.png")
        embed.set_thumbnail(url="attachment://readme.png")
        await ctx.send(embed=embed, file=image)


    @discord.ext.commands.command(name='source', aliases=['github', 'gitlab', 'git'])
    async def _source(self, ctx):
        """Hands you a link to the MrFreeze repository over on Gitlab."""
        embed = discord.Embed(color=0x00dee9)
        embed.add_field(
            name="Source code",
            value="My source code is available on [Github](https://github.com/terminalnode/mrfreeze)!")

        image = discord.File("images/source.png")
        embed.set_thumbnail(url="attachment://source.png")
        await ctx.send(embed=embed, file=image)

    @discord.ext.commands.command(name='getfreeze', aliases=['getfrozen', 'getmrfreeze', 'freezemeup', 'freezeme'])
    async def _getfreeze(self,ctx):
        """Get an invite link to invite MrFreeze to your server!"""
        botname = self.bot.user.name
        url     = f"https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot"

        embed = discord.Embed(
            color = 0x00dee9,
            description = (
                f"Here's a link for inviting me, **{botname}**, to a server." +
                f"The link will invite *this* version of me, be it the beta or regular version. Not the impostor.\n\n" +
                f"Note that **!banish** and **!region** won't function properly without the right server infrastructure (roles etc.)."))
        embed.add_field(
            name=f"Invite link for {botname}",
            value=(f"[Invite {botname} to a server.]({url})"))

        botpfp  = self.bot.user.avatar_url_as(static_format='png')
        embed.set_thumbnail(url=botpfp)
        await ctx.send(embed=embed)

    @discord.ext.commands.command(name='dummies')
    async def _dummies(self, ctx):
        """Supplies you with links to invite Ba'athman and Robin."""
        baathman_url = "https://discordapp.com/oauth2/authorize?client_id=469030362119667712&scope=bot"
        robin_url    = "https://discordapp.com/oauth2/authorize?client_id=469030900492009472&scope=bot"

        embed = discord.Embed(
            color = 0x00dee9,
            description = (
                "Here are the links for inviting Ba'athman and Robin, my arch enemies, to a server.\n\n" +
                "They don't do anything at all, but are very useful for testing kick and ban commands."))
        embed.add_field(
            name='Dummy Bots',
            value=(f"[Invite Ba'athman to a server.]({baathman_url})\n" +
                f"[Invite Robin to a server.]({robin_url})"))

        image = discord.File("images/dummies.png")
        embed.set_thumbnail(url="attachment://dummies.png")
        await ctx.send(embed=embed, file=image)

    @discord.ext.commands.command(name='todo', aliases=['TODO', 'TODOs', 'ToDo', 'ToDos', 'todos', 'whatsnext', 'whatnext'])
    async def _todos(self, ctx):
        """Supplies you with a list of my planned features."""
        url = "https://github.com/terminalnode/mrfreeze/blob/master/TODO.md"

        embed = discord.Embed(color=0x00dee9)
        embed.add_field(
            name="TODO list",
            value=f"You're a nosy one! [Here]({url})'s a list of all the \"cool\" stuff Terminal has planned for me... :sleeping:")

        image = discord.File("images/todos.png")
        embed.set_thumbnail(url="attachment://todos.png")
        await ctx.send(embed=embed, file=image)
