# Here we define all of our custom checks.

async def is_owner(ctx):
    if ctx.author.id != 154516898434908160:
        await ctx.send(ctx.author.mention +
                       ' You\'re not the boss of me, only Terminal is allowed to issue that command.')
    return ctx.author.id == 154516898434908160

async def is_mod(ctx):
    return (discord.utils.get(ctx.guild.roles, name='Administration') in ctx.author.roles)
