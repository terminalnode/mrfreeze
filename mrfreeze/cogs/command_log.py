"""Cog for logging all issued commands."""
import logging

from discord import Message
from discord.ext.commands import Cog

from mrfreeze.bot import MrFreeze
from mrfreeze.lib import colors


def setup(bot: MrFreeze) -> None:
    """Add the cog to the bot."""
    bot.add_cog(CommandLogger(bot))


class CommandLogger(Cog):
    """Cog for managing how the bot logs commands."""

    def __init__(self, bot: MrFreeze) -> None:
        """Initialize the cog."""
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        """Check if a message is a command, and log if it is."""
        if message.author.bot:
            return

        ctx = await self.bot.get_context(message)
        if ctx.command is not None:
            author = message.author
            name = f"{colors.YELLOW}{author.name}#{author.discriminator}"
            command = f"{colors.CYAN_B}{ctx.prefix}{ctx.invoked_with}"

            if ctx.guild:
                channel_name = f"{colors.GREEN}#{message.channel.name}"
                guild_name = f"{colors.MAGENTA}{message.guild.name}"
                guild_channel = f"{channel_name}{colors.CYAN} @ {guild_name}"
            else:
                guild_channel = f"{colors.MAGENTA}DMs"

            msg = f"{name} {colors.CYAN}used {command}{colors.CYAN} "
            msg += f"in {guild_channel}{colors.RESET}"
            self.logger.info(msg)
