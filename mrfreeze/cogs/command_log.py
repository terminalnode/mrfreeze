"""Cog for logging all issued commands."""
import logging

from discord import Message

from mrfreeze.lib import colors
from mrfreeze.cogs.cogbase import CogBase


def setup(bot) -> None:
    """Add the cog to the bot."""
    bot.add_cog(CommandLogger(bot))


class CommandLogger(CogBase):
    """Cog for managing how the bot logs commands."""

    def __init__(self, bot) -> None:
        """Initialize the cog."""
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    @CogBase.listener()
    async def on_message(self, message: Message) -> None:
        """Check if a message is a command, and log if it is."""
        if message.author.bot:
            return

        ctx = await self.bot.get_context(message)
        if ctx.command is not None:
            author = message.author
            name = f"{colors.YELLOW}{author.name}#{author.discriminator}"
            command = f"{colors.CYAN_B}{ctx.prefix}{ctx.invoked_with}"
            guild_name = f"{colors.MAGENTA}{message.guild.name}"
            channel_name = f"{colors.GREEN}#{message.channel.name}"

            msg = f"{name} {colors.CYAN}used {command}{colors.CYAN} "
            msg += f"in {channel_name}{colors.CYAN} @ {guild_name}{colors.RESET}"
            self.logger.info(msg)
