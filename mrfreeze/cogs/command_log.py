from .cogbase import CogBase


def setup(bot):
    bot.add_cog(CommandLogger(bot))


class CommandLogger(CogBase):
    """
    How the bot acts when errors occur.
    """

    def __init__(self, bot):
        self.bot = bot
        self.initialize_colors()

    @CogBase.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        ctx = await self.bot.get_context(message)
        if ctx.command is not None:
            author = message.author
            name = f"{self.YELLOW}{author.name}#{author.discriminator}"
            command = f"{self.CYAN_B}{ctx.prefix}{ctx.invoked_with}"
            guild_name = f"{self.MAGENTA}{message.guild.name}"
            channel_name = f"{self.GREEN}#{message.channel.name}"
            print(f"{self.current_time()} {name} {self.CYAN}used {command}" +
                  f"{self.CYAN}in {channel_name}{self.CYAN} @ {guild_name}" +
                  f"{self.RESET}")
