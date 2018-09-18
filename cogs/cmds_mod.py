import discord
from discord.ext import commands
from botfunctions import checks

# This cog is for commands restricted to mods on a server.
# It features commands such as !ban, !mute, etc.

class ModCmdsCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mute', aliases=['exile', 'banish', 'microexile', 'microbanish'])
    async def _banish(self, ctx):
        # (Micro)banish and (Micro)exile are functionally the same as mute, except with a custom message
        # and default time limit. The idea for the micro prefix is that it will work more as a statement
        # and only banish the user for a minute or so.
        # Because the mechanics of these functions are so similar - i.e. add a tag and edit the database,
        # I've chosen to clump them into the same function.
        print

    @commands.command(name='unmute', aliases=['unexile', 'unbanish'])
    async def _unmute(self, ctx):
        # This function deletes the user mute entry from userdb, and removes
        # the mute tag (antarctica tag) from the user.
        print

    @commands.command(name='ban')
    async def _ban(self, ctx):
        # This function simply bans a user from the server in which it's issued.
        print

    @commands.command(name='unban')
    async def _unban(self, ctx):
        # This function simply remover the ban of a user from the server in which it's issued.
        print

    @commands.command(name='listban')
    async def _unban(self, ctx):
        # Because it's tricky to find the exact user name/id when you can't highlight people,
        # this function exists to get easy access to the list of bans in order to unban.
        print

    @commands.command(name='kick')
    async def _kick(self, ctx):
        # This function kicks the user out of the server in which it is issued.
        print

def setup(bot):
    bot.add_cog(ModCmdsCog(bot))
