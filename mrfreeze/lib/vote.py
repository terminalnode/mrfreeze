"""Module for methods used by the vote command."""

import re
from typing import Optional
from typing import Union

from discord import Emoji
from discord.ext.commands import Bot
from discord.ext.commands import Context


def find_custom_emoji(line: str, bot: Bot) -> Union[Emoji, str]:
    """Match custom emojis in strings, or return first three characters."""
    emoji = re.match(r"<a?:\w+:(\d+)>", line)

    if emoji is None:
        return line[0:5]

    else:
        emo_id = emoji.group(1)
        emoji = bot.get_emoji(int(emo_id))
        return emoji


async def add_react(ctx: Context, react: Union[str, Emoji]) -> bool:
    """Add a single react to a message."""
    is_custom_emoji = isinstance(react, Emoji)
    did_react = False

    if is_custom_emoji:
        try:
            await ctx.message.add_reaction(react)
            did_react = True
        except Exception:
            pass

    else:
        did_react = await string_react(ctx, react)

    return did_react


async def string_react(ctx: Context, react: str) -> bool:
    """
    Try to react with a given string.

    The method is naive as to what a legitimate reactionable emoji is.
    It will first try to react to the context using the full react string.
    Then it will slice of the last character and try to react with that.
    This process continues until there's only one character left.
    """
    stop = len(react)
    while stop > 0:
        react_with = react[0:stop]

        try:
            await ctx.message.add_reaction(react_with)
            return True
        except Exception:
            pass

        stop -= 1

    return False


async def vote(ctx: Context, bot: Bot) -> None:
    """Create a handy little vote using reacts."""
    rows = ctx.message.content.split("\n")
    rows[0] = rows[0].replace("!vote ", "")
    reacts = [ find_custom_emoji(row, bot) for row in rows ]
    nitro_error = None in reacts
    results = [ await add_react(ctx, react) for react in reacts if react is not None ]

    msg: Optional[str] = None
    if nitro_error:
        msg = f"{ctx.author.mention} There seem to be some emoji there I don't have "
        msg += "access to. I need to be in the server the emoji is from."

    elif not any(results):
        msg = f"{ctx.author.mention} There's nothing I can vote for you little smudmeister!"

    if msg is not None:
        await ctx.send(msg)
