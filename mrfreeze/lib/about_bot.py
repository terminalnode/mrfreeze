"""Module for displaying bot information."""

from typing import Tuple

from discord import Embed
from discord import File
from discord.ext.commands import Context


def get_wiki_message() -> Tuple[Embed, File]:
    """Get a link to the wiki over on Github."""
    url = "https://github.com/terminalnode/mrfreeze/wiki"

    embed = Embed(color=0x00dee9)
    embed.add_field(
        name="Readme",
        value=f"Check out my wiki page [on Github]({url})!")

    image = File("images/readme.png")
    embed.set_thumbnail(url="attachment://readme.png")

    return embed, image


def get_source_message() -> Tuple[Embed, File]:
    """Get a link to the MrFreeze repository over on Github."""
    embed = Embed(color=0x00dee9)
    text = "My source code is available [on Github](https://github.com/terminalnode/mrfreeze)!"
    embed.add_field(name="Source code", value=text)

    image = File("images/source.png")
    embed.set_thumbnail(url="attachment://source.png")

    return embed, image


def get_invite_message(ctx: Context) -> Embed:
    """Get an invite link to invite MrFreeze to your server."""
    botname = ctx.bot.user.name
    url = "https://discordapp.com/oauth2/authorize?"
    url += f"client_id={ctx.bot.user.id}&scope=bot"

    text = f"Here's a link for inviting me, **{botname}**, to a server. "
    text += "The link will invite *this* version of me.\n\nNote that "
    text += "**!banish** and **!region** won't work without the right "
    text += "server infrastructure (roles etc.)."

    embed = Embed(color=0x00dee9, description=text)
    embed.add_field(
        name=f"Invite link for {botname}",
        value=(f"[Invite {botname} to a server]({url})"))

    botpic = ctx.bot.user.avatar_url_as(static_format="png")
    embed.set_thumbnail(url=botpic)
    return embed


def get_dummies_message() -> Tuple[Embed, File]:
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

    return embed, image
