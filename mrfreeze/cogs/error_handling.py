"""Cog for handling various errors that might arise when executing commands."""

import logging

from discord.ext.commands import Cog
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.lib.error_handlers import test_everything


def setup(bot: MrFreeze) -> None:
    """Add the cog to the bot."""
    bot.add_cog(ErrorHandler(bot))


class ErrorHandler(Cog):
    """How the bot acts when errors occur."""

    def __init__(self, bot: MrFreeze) -> None:
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: Exception) -> None:
        """Determine what should happen when we encounter a command error."""
        await test_everything(ctx, error, self.logger)
