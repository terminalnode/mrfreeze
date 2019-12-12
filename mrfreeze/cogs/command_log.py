"""Cog for logging all issued commands."""
from mrfreeze import colors
from mrfreeze.cogs.cogbase import CogBase


def setup(bot):
    """Add the cog to the bot."""
    bot.add_cog(CommandLogger(bot))


class CommandLogger(CogBase):
    """Cog for managing how the bot logs commands."""

    def __init__(self, bot):
        """Initialize the cog."""
        self.bot = bot

    @CogBase.listener()
    async def on_message(self, message):
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
            print(f"{self.bot.current_time()} {name} {colors.CYAN}used " +
                  f"{command}{colors.CYAN}in {channel_name}{colors.CYAN} " +
                  f"@ {guild_name}{colors.RESET}")
