"""Module for methods which change settings relating to banish."""

from typing import Optional

from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze


async def set_self_mute(ctx: Context, bot: MrFreeze, proposed_time: Optional[int]) -> None:
    """Take a proposed new self mute time for a server and try to set it."""
    mention = ctx.author.mention
    server = ctx.guild
    current = bot.get_self_mute_time(server)
    old_time = current or "the default value"
    new_time = f"{proposed_time} minutes" if proposed_time else "the default value"
    msg = None

    if proposed_time == current:
        msg = f"{mention} The self mute time for this server is already set to {new_time}."

    elif proposed_time is not None and proposed_time < 0:
        msg = f"{mention} {new_time}? Now you're just being silly."

    elif proposed_time is not None and proposed_time > 3600 * 24:
        msg = f"{mention} You're being completely unreasonable, "
        msg += f"{new_time} is more than a day!"

    else:
        setting_saved = bot.settings.set_self_mute_time(server, proposed_time)
        if setting_saved:
            msg = f"{mention} The self mute time has been changed from "
            msg += f"{old_time} to {new_time}."
        else:
            msg = f"{mention} I tried so hard, and got so far, but in the end "
            msg += f"I wasn't able to change the self mute time from {old_time} "
            msg += f"to {new_time}."

    if msg:
        await ctx.send(msg)


async def set_banish_interval(ctx: Context, bot: MrFreeze, interval: Optional[int]) -> None:
    """Take a new banish check interval for a server and try to set it."""
    mention = ctx.author.mention
    server = ctx.guild
    current = bot.settings.get_mute_interval(server)
    old_time = current or "the default value"
    new_time = f"{interval} seconds" if interval else "the default value"
    msg = None

    if interval == current:
        msg = f"{mention} The interval for this server is already set to {new_time}."

    elif interval is not None and interval < 0:
        msg = f"{mention} {new_time}? Now you're just being silly."

    elif interval is not None and interval < 5:
        msg = f"{mention} You greedy little smud you, trying to steal my CPU cycles "
        msg += "like that. Minimum interval is 5 seconds."

    elif interval is not None and interval > 60 * 5:
        msg = f"{mention} {new_time} is more than five minutes. "
        msg += "You really shouldn't set it that low."

    else:
        setting_saved = bot.settings.set_mute_interval(server, interval)

        if setting_saved:
            msg = f"{mention} The interval has been changed from {old_time} to "
            msg += f"{new_time}."
        else:
            msg = f"{mention} The interval has been changed from {old_time} to "
            msg += f"{new_time}, *BUT* for some reason I was unable to save "
            msg += f"this setting, so it will be reset to {old_time} once I restart."

    if msg:
        await ctx.send(msg)
