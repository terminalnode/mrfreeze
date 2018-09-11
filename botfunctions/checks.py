# Here we define all of our custom checks.
import discord

async def is_owner(ctx):
    # @commands.check(checks.is_owner)
    if ctx.author.id != 154516898434908160:
        await ctx.send(ctx.author.mention + ' You\'re not the boss of me, only Terminal is allowed to issue that command.')
    return ctx.author.id == 154516898434908160

async def is_mod(ctx, no_error=False):
    # @commands.check(checks.is_mod)
    mod_status = (discord.utils.get(ctx.guild.roles, name='Administration') in ctx.author.roles)
    if not mod_status and not no_error:
        await ctx.send(ctx.author.mention + ' Only mods are allowed to use that command.')
    return mod_status
