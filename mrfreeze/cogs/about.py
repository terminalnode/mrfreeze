"""A simple cog that provides some links and info to the user."""

import discord
from discord.ext.commands import Cog
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.lib import about_bot
from mrfreeze.lib import server_info
from mrfreeze.lib import user_info


def setup(bot: MrFreeze) -> None:
    """Add the cog to the bot."""
    bot.add_cog(About(bot))


whois_cmd = "whois"
whois_aliases = [ "whoami", "who" ]

serverinfo_cmd = "serverinfo"
serverinfo_aliases = [ "server" ]

wiki_cmd = "wiki"
wiki_aliases = [ "readme", "commands" ]

source_cmd = "source"
source_aliases = [ "github", "gitlab", "git" ]

getfreeze_cmd = "getfreeze"
getfreeze_aliases = [ "getfrozen", "getmrfreeze", "freezemeup", "freezeme" ]

dummies_cmd = "dummies"


class About(Cog):
    """Use these commands to unlock my deepest, darkest inner secrets."""

    def __init__(self, bot: MrFreeze) -> None:
        """Initialize the About cog."""
        self.bot = bot

    @discord.ext.commands.command(name=whois_cmd, aliases=whois_aliases)
    async def whois(self, ctx: Context) -> None:
        """Display information about yourself or a target user."""
        await user_info.run(ctx)

    @discord.ext.commands.command(name=serverinfo_cmd, aliases=serverinfo_aliases)
    async def server(self, ctx: Context) -> None:
        """Display information about the server."""
        await server_info.run(ctx)

    @discord.ext.commands.command(name=wiki_cmd, aliases=wiki_aliases)
    async def readme(self, ctx: Context) -> None:
        """Get a link to the wiki over on Github."""
        embed, image = about_bot.get_wiki_message()
        await ctx.send(embed=embed, file=image)

    @discord.ext.commands.command(name=source_cmd, aliases=source_aliases)
    async def source(self, ctx: Context) -> None:
        """Get a link to the MrFreeze repository over on Github."""
        embed, image = about_bot.get_source_message()
        await ctx.send(embed=embed, file=image)

    @discord.ext.commands.command(name=getfreeze_cmd, aliases=getfreeze_aliases)
    async def getfreeze(self, ctx: Context) -> None:
        """Get an invite link to invite MrFreeze to your server."""
        embed = about_bot.get_invite_message(ctx)
        await ctx.send(embed=embed)

    @discord.ext.commands.command(name=dummies_cmd)
    async def dummies(self, ctx: Context) -> None:
        """Get links to invite Ba'athman and Robin."""
        embed, image = about_bot.get_dummies_message()
        await ctx.send(embed=embed, file=image)
