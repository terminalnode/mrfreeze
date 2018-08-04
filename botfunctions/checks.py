async def is_owner(ctx):
    if ctx.author.id != 154516898434908160:
        await ctx.send(ctx.author.mention +
                       ' You\'re not the boss of me, only Terminal is allowed to issue that command.')
    return ctx.author.id == 154516898434908160
