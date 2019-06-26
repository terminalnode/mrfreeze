import discord      # Required to check for a lot of different discord exceptions
import traceback    # Debugging
import sys          # Debugging

# If buckets are ever implemented again:
# from discord.ext.commands.cooldowns import BucketType
# import inflect
def setup(bot):
    bot.add_cog(CommandLogCog(bot))

class CommandLogCog(discord.ext.commands.Cog, name='CommandLogger'):
    """How the bot acts when errors occur."""

    def __init__(self, bot):
        self.bot = bot

    @discord.ext.commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:  return

        ctx = await self.bot.get_context(message)
        if ctx.command != None:
            print(f"{self.bot.current_time()} {self.bot.YELLOW}{message.author.name}#{message.author.discriminator} " +
                f"{self.bot.CYAN}used {self.bot.CYAN_B}{ctx.prefix}{ctx.invoked_with} {self.bot.CYAN}in " +
                f"{self.bot.GREEN}#{message.channel.name}{self.bot.CYAN} @ {self.bot.MAGENTA}{message.guild.name}{self.bot.RESET}")
