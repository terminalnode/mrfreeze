"""A cog for the owner to dynamically change the log levels."""

import logging
from typing import Optional

from discord.ext import commands
from discord.ext.commands import Cog
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.lib.checks import is_owner


def setup(bot: MrFreeze) -> None:
    """Add the cog to the bot."""
    bot.add_cog(LogLevel(bot))


class LogLevel(Cog):
    """Commands used for changing the log level of a component."""

    def __init__(self, bot: MrFreeze) -> None:
        """Initialize the About cog."""
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    @commands.command(name="infolog")
    @commands.check(is_owner)
    async def infolog(self, ctx: Context, module: Optional[str]) -> None:
        """Set log level to INFO for a given module."""
        if module:
            self.logger.info(f"Setting log level to INFO for {module}")
            logging.getLogger(module).setLevel(logging.INFO)

    @commands.command(name="warnlog", aliases=["warninglog"])
    @commands.check(is_owner)
    async def warnlog(self, ctx: Context, module: Optional[str]) -> None:
        """Set log level to WARNING for a given module."""
        if module:
            self.logger.info(f"Setting log level to WARNING for {module}")
            logging.getLogger(module).setLevel(logging.WARNING)

    @commands.command(name="debuglog")
    @commands.check(is_owner)
    async def debuglog(self, ctx: Context, module: Optional[str]) -> None:
        """Set log level to DEBUG for a given module."""
        if module:
            self.logger.info(f"Setting log level to DEBUG for {module}")
            logging.getLogger(module).setLevel(logging.DEBUG)

    @commands.command(name="errorlog")
    @commands.check(is_owner)
    async def errorlog(self, ctx: Context, module: Optional[str]) -> None:
        """Set log level to ERROR for a given module."""
        if module:
            self.logger.info(f"Setting log level to ERROR for {module}")
            logging.getLogger(module).setLevel(logging.ERROR)

    @commands.command(name="criticallog")
    @commands.check(is_owner)
    async def criticallog(self, ctx: Context, module: Optional[str]) -> None:
        """Set log level to CRITICAL for a given module."""
        if module:
            self.logger.info(f"Setting log level to CRITICAL for {module}")
            logging.getLogger(module).setLevel(logging.CRITICAL)
