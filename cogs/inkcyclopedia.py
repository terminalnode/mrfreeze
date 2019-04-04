import discord
from discord.ext import commands
from botfunctions import native

class InkcyclopediaCog(commands.Cog, name='Inkcyclopedia'):
    """Type an ink inside {curly brackets} and I'll tell you what it looks like!"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        pass

def setup(bot):
    bot.add_cog(InkcyclopediaCog(bot))
