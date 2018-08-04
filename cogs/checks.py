import discord, sys, os
from discord.ext import commands

class ChecksCog:
    def __init__(self, bot):
        self.bot = bot

    async def is_owner(ctx):
        return ctx.author.id == 154516898434908160

def setup(bot):
    bot.add_cog(ChecksCog(bot))
