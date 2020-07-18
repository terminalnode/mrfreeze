"""A simple cog that provides some links and info to the user."""

from typing import List

import discord
from discord import Embed
from discord import File
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.cogs.cogbase import CogBase


def setup(bot: MrFreeze) -> None:
    """Add the cog to the bot."""
    bot.add_cog(About(bot))


source_aliases: List[str] = [
    "github", "gitlab", "git"]
getfreeze_aliases: List[str] = [
    "getfrozen", "getmrfreeze", "freezemeup", "freezeme"]


class About(CogBase):
    """Use these commands to unlock my deepest, darkest inner secrets."""

    def __init__(self, bot: MrFreeze) -> None:
        """Initialize the About cog."""
        self.bot = bot

    @discord.ext.commands.command(name="wiki", aliases=[ "readme", "commands" ])
    async def readme(self, ctx: Context) -> None:
        """Get a link to the wiki over on Github."""
        url = "https://github.com/terminalnode/mrfreeze/wiki"

        embed = Embed(color=0x00dee9)
        embed.add_field(
            name="Readme",
            value=f"Check out my wiki page [on Github]({url})!")

        image = File("images/readme.png")
        embed.set_thumbnail(url="attachment://readme.png")
        await ctx.send(embed=embed, file=image)

    @discord.ext.commands.command(name="source", aliases=source_aliases)
    async def source(self, ctx: Context) -> None:
        """Get a link to the MrFreeze repository over on Github."""
        embed = Embed(color=0x00dee9)
        text = "My source code is available [on Github](https://github.com/terminalnode/mrfreeze)!"
        embed.add_field(name="Source code", value=text)

        image = File("images/source.png")
        embed.set_thumbnail(url="attachment://source.png")
        await ctx.send(embed=embed, file=image)

    @discord.ext.commands.command(name="getfreeze", aliases=getfreeze_aliases)
    async def getfreeze(self, ctx: Context) -> None:
        """Get an invite link to invite MrFreeze to your server."""
        botname = self.bot.user.name
        url = "https://discordapp.com/oauth2/authorize?"
        url += f"client_id={self.bot.user.id}&scope=bot"

        text = f"Here's a link for inviting me, **{botname}**, to a server. "
        text += "The link will invite *this* version of me.\n\nNote that "
        text += "**!banish** and **!region** won't work without the right "
        text += "server infrastructure (roles etc.)."

        embed = Embed(color=0x00dee9, description=text)
        embed.add_field(
            name=f"Invite link for {botname}",
            value=(f"[Invite {botname} to a server]({url})"))

        botpic = self.bot.user.avatar_url_as(static_format="png")
        embed.set_thumbnail(url=botpic)
        await ctx.send(embed=embed)

    @discord.ext.commands.command(name="dummies")
    async def dummies(self, ctx: Context) -> None:
        """Get links to invite Ba'athman and Robin."""
        baathman_url = "https://discordapp.com/oauth2/authorize?"
        baathman_url += "client_id=469030362119667712&scope=bot"
        robin_url = "https://discordapp.com/oauth2/authorize?"
        robin_url += "client_id=469030900492009472&scope=bot"

        embed_text = "Here are the links for inviting Ba'athman and Robin, my "
        embed_text += "arch enemies, to a server.\n\nThey don't do anything "
        embed_text += "whatsoever, but are very useful for testing purposes "
        embed_text += "such as trying out kick and ban commands."

        invite_text = f"[Invite Ba'athman to a server]({baathman_url})\n"
        invite_text += f"[Invite Robin to a server]({robin_url})"

        embed = Embed(color=0x00dee9, description=embed_text)
        embed.add_field(name="Dummy Bots", value=invite_text)

        image = File("images/dummies.png")
        embed.set_thumbnail(url="attachment://dummies.png")
        await ctx.send(embed=embed, file=image)
