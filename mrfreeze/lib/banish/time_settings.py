"""Module for methods which change settings relating to banish."""

from typing import Optional

from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze


async def set_self_mute(ctx: Context, bot: MrFreeze, proposed_time: Optional[int]) -> None:
    """Take the context of a command trying to change the self mute time and do something."""
    mention = ctx.author.mention
    server = ctx.guild
    current_time = bot.get_self_mute_time(server)
    msg = None

    if proposed_time is None and current_time is not None:
        setting_saved = bot.settings.set_self_mute_time(server, proposed_time)

        if setting_saved:
            msg = f"{mention} The self mute time has been changed from "
            msg += f"{current_time} to using the bot default value."
        else:
            msg = f"{mention} I tried so hard, and got so far, but in the end "
            msg += f"I wasn't able to change the self mute time from {current_time} "
            msg += "to using the bot default value."

    elif proposed_time is None:
        msg = f"{mention} {proposed_time} minutes? Now you're just being silly."

    elif proposed_time == current_time:
        msg = f"{mention} The self mute time for this server is already set to {proposed_time}."

    elif proposed_time < 0:
        msg = f"{mention} {proposed_time} minutes? Now you're just being silly."

    elif proposed_time > 3600 * 24:
        msg = f"{mention} You're being completely unreasonable, "
        msg += f"{proposed_time} minutes is more than a day!"

    else:
        current: str
        if current_time:
            current = f"{current_time}"
        else:
            current = "the bot default value"

        setting_saved = bot.settings.set_self_mute_time(server, proposed_time)

        if setting_saved:
            msg = f"{mention} The self mute time has been changed from "
            msg += f"{current} to {proposed_time} minutes."
        else:
            msg = f"{mention} I tried so hard, and got so far, but in the end "
            msg += f"I wasn't able to change the self mute time from {current} "
            msg += f"to {proposed_time} minutes."

    # Send the message if we have one
    if msg:
        await ctx.send(msg)
