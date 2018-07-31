import discord, re
from discord.ext import commands

# Unlike it's predecessor, this one will look through all messages for
# temperatures and convert them.

class TempConverterCog():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='placeholder')
    async def _placeholder(self, ctx):
        # This regex expression will find any temperature expression in a string.
        # re.search('\d+[,.]?\d+ ?(degrees|c|f|°c|°f|k|°k|r|°r)[^\w]?', string)
        # It will match generic degrees, celcius, fahrenheit, kelvin and rankine
        pass

def setup(bot):
    bot.add_cog(TempConverterCog(bot))
