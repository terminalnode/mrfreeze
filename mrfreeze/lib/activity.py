"""Module for methods used by the activity command."""

from typing import Optional
from typing import Tuple

from discord import Activity
from discord import ActivityType
from discord.ext.commands import Bot
from discord.ext.commands import Context

# Standard values
max_activity_length = 30

# Activity tuples
playing_activity = (ActivityType.playing, "playing")
streaming_activity = (ActivityType.streaming, "streaming")
listening_activity = (ActivityType.listening, "listening to")
watching_activity = (ActivityType.watching, "watching")
default_activity = listening_activity


def get_chosen_activity(invocation: str) -> Tuple[ActivityType, str]:
    """
    Use the command invocation to determine which activity type to use.

    Returns two values, the activity type and a text description of the activity,
    such as 'playing' or 'listening to'.
    """
    if "play" in invocation or "gam" in invocation:
        return playing_activity
    elif "stream" in invocation:
        return streaming_activity
    elif "listen" in invocation:
        return listening_activity
    elif "watch" in invocation:
        return watching_activity

    return default_activity


def extract_activity(
        args: Tuple[str, ...],
        activity_type: ActivityType) -> Tuple[Optional[Activity], str]:
    """Create the activity we're changing to."""
    joint_args = " ".join(args)
    if len(joint_args) > max_activity_length:
        return (None, joint_args)

    return (Activity(name=joint_args, type=activity_type), joint_args)


async def set_activity(ctx: Context, bot: Bot, args: Tuple[str, ...]) -> None:
    """Dictate what text should be displayed under my nick."""
    chosen_activity: ActivityType
    reply_activity: str
    new_activity: Optional[Activity]
    activity_name: str

    chosen_activity, reply_activity = get_chosen_activity(ctx.invoked_with)
    new_activity, activity_name = extract_activity(args, chosen_activity)
    activity_length = len(activity_name)

    success = False
    if new_activity is not None:
        await bot.change_presence(activity=new_activity)
        success = True

    msg: Optional[str] = None
    if success:
        msg = f"{ctx.author.mention} OK then, I guess I'm "
        msg += f"**{reply_activity} {new_activity.name}** now."

    elif len(args) == 0:
        msg = f"{ctx.author.mention} You didn't tell me what to do."

    elif len(activity_name) >= max_activity_length:
        msg = f"{ctx.author.mention} That activity is stupidly long ({activity_length}). "
        msg += f"The limit is {max_activity_length} characters."

    if msg:
        await ctx.send(msg)
