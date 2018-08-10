import discord
from discord.ext import commands
from botfunctions import checks

# This cog is for commands restricted to mods on a server.
# It features commands such as !ban, !mute, etc.

class ModCmdsCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='banish')
    async def _banish(self, ctx):
        print

    @commands.command(name='ban')
    async def _ban(self, ctx):
        print

    @commands.command(name='unban')
    async def _unban(self, ctx):
        print

    @commands.command(name='mute')
    async def _mute(self, ctx):
        print

    @commands.command(name='unmute')
    async def _unmute(self, ctx):
        print

    @commands.command(name='kick')
    async def _kick(self, ctx):
        print

def setup(bot):
    bot.add_cog(ModCmdsCog(bot))
