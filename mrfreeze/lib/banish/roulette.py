"""Module for the roulette command."""

import asyncio
import datetime
import random

import discord
from discord.ext.commands import Context

from mrfreeze.cogs.coginfo import CogInfo
from mrfreeze.lib.banish import mute_db


async def roulette(ctx: Context, cog: CogInfo) -> None:
    """Roll the dice and test your luck, banish or nothing."""
    if cog.bot and cog.logger:
        bot = cog.bot
    else:
        return

    member = ctx.author
    mention = member.mention
    is_mod = ctx.author.guild_permissions.administrator
    trash_channel = await bot.get_trash_channel(ctx.guild)

    # Skip if user is already muted
    if await bot.get_mute_role(ctx.guild) in ctx.author.roles and not is_mod:
        await ctx.send(f"{mention} Looks to me like you've already lost the game.")
        return

    # Skip if message isn't sent from trash channel
    elif ctx.channel != trash_channel and not is_mod:
        await ctx.send(f"Please only use that command in the {trash_channel.mention}... smud.")
        return

    # Roll the dice!
    if random.randint(1, 6) == 1:
        await lost_roulette(ctx, cog)

    else:
        response = await ctx.send(f"Sorry chat, seems {mention} will live to see another day.")
        await asyncio.sleep(5)
        await ctx.message.delete()
        await response.delete()


async def lost_roulette(ctx: Context, cog: CogInfo) -> None:
    """Do what happens when the user loses."""
    if cog.bot and cog.logger:
        bot = cog.bot
        logger = cog.logger
    else:
        return

    mention = ctx.author.mention
    banish_time = random.randint(1, 5)
    duration = datetime.timedelta(minutes = banish_time)
    end_date = datetime.datetime.now() + duration
    msg = r"Not sure what happened, you probably died or something. ¯\_(ツ)_/¯"

    msg = get_losing_message(banish_time, mention)

    if ctx.author.guild_permissions.administrator:
        msg += "\n\nOr that's what would've happened if you weren't a "
        msg += "mod who's banished FROM Antarctica."

    else:
        error = await mute_db.carry_out_banish(bot, ctx.author, logger, end_date)

        if isinstance(error, discord.HTTPException):
            msg = f"While {mention} did fail and hurt themselves spectacularly in the "
            msg += "roulette there's not much I can do about it due to some stupid HTTP error."
        elif isinstance(error, discord.Forbidden):
            msg = f"While {mention} did fail and hurt themselves spectacularly in the "
            msg += "roulette there's not much I can do about it because I'm not allowed "
            msg += "to banish people."
        elif isinstance(error, Exception):
            msg = f"While {mention} did fail and hurt themselves spectacularly in the "
            msg += "roulette there's not much I can do about it because, uh, reasons. "
            msg += "I don't know."

    await ctx.send(msg)


def get_losing_message(banish_time: int, mention: str) -> str:
    """Return a message based on the banish time."""
    if banish_time == 1:
        msg = f"{mention} rolls the dice, the gun doesn't fire but somehow "
        msg += "they manage to hurt themselves with it anyway. A minute in "
        msg += "Antarctica and they'll be good as new!"

    elif banish_time == 2:
        msg = f"{mention} rolls the dice, but the gun misfires and explodes in "
        msg += "their hand. Better put some ice on that, should be fine in 2 minutes."

    elif banish_time == 3:
        msg = f"{mention} rolls the dice, slips and shoots themselves in the leg. "
        msg += "The nearest hospital they can afford is in Antarctica, where "
        msg += "they will be spending the next 3 minutes."

    elif banish_time == 4:
        msg = f"{mention} rolls the dice of death, but the gun is jammed. "
        msg += "As they're looking down the barrel something blows up and "
        msg += "hits them in the eye. 4 minutes in Antarctica!"

    else:
        msg = f"{mention} rolls a headshot on the dice of death! 5 minutes in Antarctica!"

    return msg
