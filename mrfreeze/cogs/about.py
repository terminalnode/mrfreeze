"""A simple cog that provides some links and info to the user."""

from typing import List

import discord
from discord import Embed
from discord import File
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.cogs.cogbase import CogBase


def setup(bot):
    """Add the cog to the bot."""
    bot.add_cog(About(bot))


source_aliases: List[str] = [
        "github", "gitlab", "git"]
getfreeze_aliases: List[str] = [
        "getfrozen", "getmrfreeze", "freezemeup", "freezeme"]
todo_aliases: List[str] = [
        "TODO", "TODOs", "ToDo", "ToDos", "todos", "whatsnext", "whatnext"]


class About(CogBase):
    """Use these commands to unlock my deepest, darkest inner secrets."""

    def __init__(self, bot: MrFreeze):
        """Initialize the About cog."""
        self.bot = bot
        self.initialize_colors()

    @discord.ext.commands.command(name="readme")
    async def readme(self, ctx: Context) -> None:
        """Get a link to the readme file over on Github."""
        url = "https://github.com/terminalnode/mrfreeze/blob/master/README.md"

        embed = Embed(color=0x00dee9)
        embed.add_field(
            name="Readme",
            value=f"My readme file is available [on Github]({url})!")

        image = File("images/readme.png")
        embed.set_thumbnail(url="attachment://readme.png")
        await ctx.send(embed=embed, file=image)

    @discord.ext.commands.command(name="source", aliases=source_aliases)
    async def source(self, ctx: Context) -> None:
        """Get a link to the MrFreeze repository over on Github."""
        embed = Embed(color=0x00dee9)
        embed.add_field(
            name="Source code",
            value=("My source code is available [on " +
                   "Github](https://github.com/terminalnode/mrfreeze)!")
        )

        image = File("images/source.png")
        embed.set_thumbnail(url="attachment://source.png")
        await ctx.send(embed=embed, file=image)

    @discord.ext.commands.command(name="getfreeze", aliases=getfreeze_aliases)
    async def getfreeze(self, ctx: Context) -> None:
        """Get an invite link to invite MrFreeze to your server."""
        botname = self.bot.user.name
        url = ("https://discordapp.com/oauth2/authorize?" +
               f"client_id={self.bot.user.id}&scope=bot")

        embed = Embed(
            color=0x00dee9,
            description=(
                f"Here's a link for inviting me, **{botname}**, to a server." +
                "The link will invite *this* version of me, be it the beta " +
                "or regular version. Not the impostor.\n\nNote however that " +
                "**!banish** and **!region** won't work without the right " +
                "server infrastructure (roles etc.)."))
        embed.add_field(
            name=f"Invite link for {botname}",
            value=(f"[Invite {botname} to a server]({url})"))

        botpic = self.bot.user.avatar_url_as(static_format="png")
        embed.set_thumbnail(url=botpic)
        await ctx.send(embed=embed)

    @discord.ext.commands.command(name="dummies")
    async def dummies(self, ctx: Context) -> None:
        """Get links to invite Ba'athman and Robin."""
        baathman_url: str = ("https://discordapp.com/oauth2/authorize?" +
                             "client_id=469030362119667712&scope=bot")
        robin_url: str = ("https://discordapp.com/oauth2/authorize?" +
                          "client_id=469030900492009472&scope=bot")

        embed = Embed(
            color=0x00dee9,
            description=(
                "Here are the links for inviting Ba'athman and Robin, my " +
                "arch enemies, to a server.\n\nThey don't do anything " +
                "whatsoever, but are very useful for testing purposes " +
                "such as trying out kick and ban commands.")
        )
        embed.add_field(
            name="Dummy Bots",
            value=(f"[Invite Ba'athman to a server]({baathman_url})\n" +
                   f"[Invite Robin to a server]({robin_url})"))

        image = File("images/dummies.png")
        embed.set_thumbnail(url="attachment://dummies.png")
        await ctx.send(embed=embed, file=image)

    @discord.ext.commands.command(name="todo", aliases=todo_aliases)
    async def todos(self, ctx: Context) -> None:
        """Get a list of planned features for the bot."""
        url = "https://github.com/terminalnode/mrfreeze/blob/master/TODO.md"

        embed = Embed(color=0x00dee9)
        embed.add_field(
            name="TODO list",
            value=(f"You're a nosy one! [Here]({url})'s a list of all the " +
                   "\"cool\" stuff Terminal has planned for me... :sleeping:")
        )

        image = File("images/todos.png")
        embed.set_thumbnail(url="attachment://todos.png")
        await ctx.send(embed=embed, file=image)
