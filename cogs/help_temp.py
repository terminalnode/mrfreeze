import discord
from discord.ext import commands

# Unlike it's predecessor, this one will look through all messages for
# temperatures and convert them.

class TempConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='temp', aliases=['temperature', 'tempconversion', 'tempconvert'])
    async def _temp(self, ctx, *args):
        # The function itself isn't really a command, the bot continuously listens for temperature
        # statements and converts them accordingly. This command is more of a help file.
        # If your editor has soft wrap, enable it because this will look like shit otherwise.
        await ctx.send(ctx.author.mention + ' Check your DMs! The help for temperature conversion is a bit long so I won\'t be posting it here.')
        await ctx.author.send('''You've tried to invoke the temperature conversion command, unfortunately there is no such command. Instead I will continuously look through all messages you send to the server and search for temperature statements. These statements usually look something like this:
"Oh geez it's so warm here, over 80 degrees."
"It's like -10 c outside and I'm *freezing* to death."
"What's 370,5 kelvin in civilised units?"
"5.2 celcius???"
and so on and so on. I will detect both abbreviated and unabbreviated units and decimals both written as dots (.) or commas (,). So basically just write whatever you wanted to write to start with and I'll handle the temperature conversions for you.

If you want to do a specific conversion, you can also write something like "5 c in k", "2.2 kelvin in rankine" or "1337,0 rankine in c". The possibilities are endless!''')

def setup(bot):
    bot.add_cog(TempConverterCog(bot))
