"""Module for the region command."""

import datetime
from typing import Tuple

import discord
from discord.ext.commands import Context

from mrfreeze.cogs.coginfo import CogInfo
from mrfreeze.cogs.coginfo import InsufficientCogInfo
from mrfreeze.lib.banish import mute_db


regional_aliases = {
    "Asia": [
        "asia", "china", "japan", "thailand", "korea"
    ], "Europe": [
        "europe", "united kingdom", "gb", "great britain", "scandinavia", "germany",
        "sweden", "norway", "spain", "france", "italy", "ireland", "poland", "russia",
        "finland", "estonia", "scotland", "scottland", "portugal"
    ], "North America": [
        "north america", "us", "canada", "mexico", "na", "usa", "united states"
    ], "Africa": [
        "africa", "kongo", "uganda"
    ], "Oceania": [
        "oceania", "australia", "new zealand"
    ], "South America": [
        "south america", "argentina", "chile", "brazil", "peru"
    ], "Middle East": [
        "middleeast", "middle-east", "midleeast", "midle-east", "middleast", "midleast",
        "mesa", "saudi", "saudiarabia", "arabia", "arabian", "middle east", "midle east"
    ]
}


antarctica_spellings = (
    "anarctica", "antarctica", "antartica", "anartica",
    "anctartica", "anctarctica", "antacrtica")


async def region_cmd(ctx: Context, cog: CogInfo, args: Tuple[str, ...]) -> None:
    """Assign yourself a colourful regional role."""
    args = tuple([ a.lower() for a in args ])

    if len(args) == 0 or "help" in args:
        msg = "Type !region followed by your region, this will assign you a regional role "
        msg += "with an associated snazzy colour for your nick. These roles are not "
        msg += "highlightable and only serve to show people where you're from. \n\n"
        msg += "The available regions are:\n"
        msg += " - Asia\n - Europe\n - North America\n - South America\n"
        msg += " - Africa\n - Oceania\n - Middle East"
        await ctx.send(msg)
        return

    if "list" in args:
        msg = "Available regions:\n"
        msg += " - Asia\n - Europe\n - North America\n - South America\n"
        msg += " - Africa\n - Oceania\n - Middle East"
        await ctx.send(msg)
        return

    if await region_antarctica(ctx, cog, args):
        return

    await set_region(ctx, cog, args)


async def region_antarctica(ctx: Context, cog: CogInfo, args: Tuple[str, ...]) -> bool:
    """
    Analyze arguments to see if user tried to set region to Antarctica.

    If they did, the method will return True, banish them and send some snarky repyl.
    Otherwise it returns False.
    """
    if cog.bot and cog.logger:
        bot = cog.bot
        logger = cog.logger
    else:
        raise InsufficientCogInfo()

    # Check if the user tried to set region to Antarctica
    said_antarctica = False
    for variant in antarctica_spellings:
        if variant in args:
            said_antarctica = True
            spelling = variant
            break

    if not said_antarctica:
        return False

    # User confirmed to have tried to set region to Antarctica
    # Initiating punishment
    reply = f"{ctx.author.mention} is a filthy *LIAR* claiming to live in Antarctica. "

    if spelling == "antarctica":
        duration = datetime.timedelta(minutes = 10)
        end_date = datetime.datetime.now() + duration
        duration = bot.parse_timedelta(duration)
        reply += "I'll give them what they want and banish them to that "
        reply += "frozen hell for ten minutes!"

    else:
        duration = datetime.timedelta(minutes = 20)
        end_date = datetime.datetime.now() + duration
        duration = bot.parse_timedelta(duration)
        reply += f"What's more, they spelled it *{spelling.capitalize()}* "
        reply += "instead of *Antarctica*... 20 minutes in Penguin school "
        reply += "ought to teach them some manners!"

    # Carry out the banish with resulting end date
    error = await mute_db.carry_out_banish(
        bot,
        ctx.author,
        logger,
        end_date
    )
    if isinstance(error, Exception):
        reply = f"{ctx.author.mention} is a filthy *LIAR* claiming to live in Antarctica. "
        reply += "Unfortunately there doesn't seem to be much I can do about that. Not sure "
        reply += "why. Some kind of system malfunction or whatever."

    await ctx.send(reply)
    return True


async def set_region(ctx: Context, cog: CogInfo, args: Tuple[str, ...]) -> None:
    """
    Set the region of a user based on what they said.

    Determine which region the user tried to set using the !region command,
    then set that region (if found) and send an appropriate response. If
    the region isn't found don't set a role, just send an appropriate response.
    """
    if cog.regions:
        regions = cog.regions[ctx.guild.id]
    else:
        raise InsufficientCogInfo()

    author_roles = [ i.id for i in ctx.author.roles if i.name not in regions.keys() ]
    all_args = " ".join(args)

    found_region = False
    valid_region = True
    for region in regional_aliases:
        if found_region:
            break

        for alias in regional_aliases[region]:
            if alias in all_args:
                author_roles.append(regions[region])
                valid_region = regions[region] is not None
                new_role_name = region
                found_region = True
                break

    if found_region and valid_region:
        new_roles = [ discord.Object(id=i) for i in author_roles ]
        await ctx.author.edit(roles=new_roles)

        msg = f"{ctx.author.mention} You've been assigned a new role, "
        msg += f"welcome to {new_role_name}!"
    else:
        msg = f"{ctx.author.mention} I couldn't find a match for {' '.join(args)}.\n"
        msg += "Please check your spelling or type **!region list** for a list of "
        msg += "available regions."
    await ctx.send(msg)
