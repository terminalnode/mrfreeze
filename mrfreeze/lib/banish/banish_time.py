"""Module for handling the banish time command."""
import datetime
from typing import List
from typing import Optional

from discord import Member
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.cogs.coginfo import CogInfo
from mrfreeze.cogs.coginfo import InsufficientCogInfo
from mrfreeze.lib.banish import mute_db


async def run_command(ctx: Context, coginfo: CogInfo, user: Optional[Member]) -> None:
    """Run the banish time command, telling the user how long they have left."""
    if coginfo.bot:
        bot: MrFreeze = coginfo.bot
    else:
        raise InsufficientCogInfo

    user = user or ctx.author
    banish_list: List[mute_db.BanishTuple]
    banish_list = mute_db.mdb_fetch(bot, user)
    mention = user.mention

    msg: Optional[str] = None
    if not banish_list:
        msg = f"{mention} is not banished right now."

    else:
        until = banish_list[0].until
        now = datetime.datetime.now()

        if until and until < now:
            msg = f"{mention} is due for unbanishment. Hold on a sec."

        else:
            left = bot.parse_timedelta(until - now) if until else "an eternity"
            msg = f"{mention} has about **{left}** left to go."

    if msg:
        await ctx.send(msg)
