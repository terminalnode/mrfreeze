"""Handles messages"""

from typing import List
import logging

import discord
from discord import Embed
from discord import File
from discord import TextChannel
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.cogs.cogbase import CogBase


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


def setup(bot):
    """Add the cog to the bot."""
    bot.add_cog(Messages(bot))


class Messages(CogBase):
    """Handles messages"""

    def __init__(self, bot: MrFreeze):
        """Initialize the Messages cog."""
        self.bot = bot

    @discord.ext.commands.command(name="copy")
    async def copy(
                self,
                ctx: Context,
                msg_id: str,
                destination_channel_name: str
            ) -> None:
        """Copies specified message to specified channel."""
        logger.info("Moving message")
        logger.debug(f"ctx: {ctx.__dict__}")
        logger.debug(f"msg_id: {msg_id}")
        logger.debug(f"destination_channel_name: {destination_channel_name}")

        command_channel = ctx.message.channel
        target_message = await command_channel.fetch_message(msg_id)
        logger.debug(f"target_message: {target_message}")

        destination_channel = discord.utils.get(
            ctx.message.guild.channels,
            name=destination_channel_name
        )
        logger.debug(f"destination_channel: {destination_channel}")

        embed = Embed(
            color=0x00dee9,
            description=target_message.content
        )
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.avatar_url
        )
        embed.set_thumbnail(url=ctx.author.avatar_url)

        await destination_channel.send(embed=embed)