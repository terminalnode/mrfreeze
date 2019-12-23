"""A simple cog that provides some links and info to the user."""

from typing import List

import discord
from discord import Embed
from discord import File
from discord import TextChannel
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.cogs.cogbase import CogBase


def setup(bot):
    """Add the cog to the bot."""
    bot.add_cog(Move(bot))


class Move(CogBase):
    #TODO Add docstring

    def __init__(self, bot: MrFreeze):
        """Initialize the About cog."""
        self.bot = bot

    @discord.ext.commands.command(name="move")
    async def move(self, ctx: Context, msg_id: str, destination_channel: str) -> None:
        # TODO add docstring
        print("Moving")
        print(f"ctx: {ctx.__dict__}")
        print(f"msg_id: {msg_id}")
        print(f"destination_channel: {destination_channel}")

        command_channel = ctx.message.channel
        target_message = await command_channel.fetch_message(msg_id)

        print("Got targets and info")
        print(f"command_channel: {command_channel}")
        print(f"target_message: {target_message}")
        print(f"author: {target_message.author}")
        print(f"content: {target_message.content}")

        print(f"guild channels: {ctx.message.guild.channels}")

        target_channel = discord.utils.get(ctx.message.guild.channels, name=destination_channel)

        print(f"target_channel: {target_channel}")

        embed = Embed(color=0x00dee9)
        embed.add_field(
            name="Author",
            value=target_message.author.name
        )
        embed.add_field(
            name="Content",
            value=target_message.content
        )

        await target_channel.send(embed=embed)