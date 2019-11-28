import discord  # Required to compare called to discord.member.Member

async def is_owner(ctx):
    # @commands.check(checks.is_owner)
    is_owner = await ctx.bot.is_owner(ctx.author)
    if not is_owner:
        await ctx.send(f"{ctx.author.mention} You're not the boss of me! " +
            "<@!154516898434908160> Help I'm being opressed!!")
    return is_owner

async def is_mod(caller):
    # @commands.check(checks.is_mod)
    # This check can also be used as a command with a member object,
    # depending on the input, output may vary.
    member_call = isinstance(caller, discord.member.Member)

    if member_call:
        # caller is a member object
        mod_status = caller.guild_permissions.administrator

    else:
        # caller is a context object
        if caller.guild == None:
            await ctx.send(f"Don't you try to sneak into my DMs and mod me!")
            return False

        mod_status = caller.author.guild_permissions.administrator
        if not mod_status:
            await caller.send(f"{caller.author.mention} Only mods are allowed to use that command.")

    return mod_status

async def always_deny(ctx):
    # @commands.check(checks.always_deny)
    # This is for debugging, always returns False.
    return False

async def always_allow():
    # @commands.check(checks.always_deny)
    # This is for debugging, always returns True.
    return True
