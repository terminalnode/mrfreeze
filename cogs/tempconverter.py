import discord, re
from discord.ext import commands

# Unlike it's predecessor, this one will look through all messages for
# temperatures and convert them.

class TempConverterCog():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='placeholder')
    async def _placeholder(self, ctx):
        pass

def setup(bot):
    bot.add_cog(TempConverterCog(bot))
