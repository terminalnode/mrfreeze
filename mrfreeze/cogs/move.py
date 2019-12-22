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
        print(f"msg_id: {id}")
        print(f"destination_channel: {destination_channel}")

        for cmd in dir(self.bot):
            if 'message' in cmd.lower():
                print(cmd)

        embed = Embed(color=0x00dee9)
        embed.add_field(
            name="Move",
            value="Move field value"
        )

        await ctx.send(embed=embed)