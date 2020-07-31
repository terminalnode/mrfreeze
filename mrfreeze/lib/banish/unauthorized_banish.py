"""Module for handling unauthorized mute/banish attempts."""
import datetime
from logging import Logger

import discord
from discord.ext.commands import CheckFailure
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.cogs.coginfo import CogInfo
from mrfreeze.cogs.coginfo import InsufficientCogInfo
from mrfreeze.lib import default
from mrfreeze.lib import time
from mrfreeze.lib.banish import mute_db
from mrfreeze.lib.banish.templates import MuteResponseType
from mrfreeze.lib.banish.templates import TemplateEngine


async def run_command(
    ctx: Context,
    coginfo: CogInfo,
    template_engine: TemplateEngine,
    error: Exception
) -> None:
    """
    Trigger on unauthorized banish, i.e. when a non-administrator try to banish people.

    When _banish() encounters an error this method is automatically triggered. If the error
    is an instance of discord.ext.commands.CheckFailure the user will be punished accordingly,
    if not the error is raised again.

    There are four relevant templates that can be used when sending the response.
    USER_NONE     User invoked mute with no arguments
    USER_SELF     User tried muting themselves
    USER_USER     User tried muting other user(s)
    USER_MIXED    User tried musing themselves and other user(s)
    """
    if coginfo.bot and coginfo.default_self_mute_time and coginfo.logger:
        bot: MrFreeze = coginfo.bot
        default_self_mute_time: int = coginfo.default_self_mute_time
        logger: Logger = coginfo.logger
    else:
        raise InsufficientCogInfo

    if not isinstance(error, CheckFailure):
        # Only run this on Check Failure.
        return

    mentions = ctx.message.mentions
    author = ctx.author
    server = ctx.guild

    none     = (len(mentions) == 0)
    selfmute = (len(mentions) == 1 and author in mentions)
    mix      = (not selfmute and author in mentions)
    user     = (not selfmute and not mix and len(mentions) > 0)
    fails    = default.mentions_list([ mention for mention in mentions if mention != author ])

    if none:
        template = MuteResponseType.USER_NONE
    elif selfmute:
        template = MuteResponseType.USER_SELF
    elif user:
        template = MuteResponseType.USER_USER
    elif mix:
        template = MuteResponseType.USER_MIXED

    self_mute_time: int = bot.get_self_mute_time(server) or default_self_mute_time
    duration = datetime.timedelta(minutes = float(self_mute_time))
    end_date = datetime.datetime.now() + duration
    duration = time.parse_timedelta(duration)

    # Carry out the banish with resulting end date
    banish_error = await mute_db.carry_out_banish(
        bot,
        author,
        logger,
        end_date
    )
    error_msg = "unspecified error"

    if isinstance(banish_error, Exception):
        if isinstance(banish_error, discord.Forbidden):
            error_msg = "**a lack of privilegies**"
        elif isinstance(banish_error, discord.HTTPException):
            error_msg = "**an HTTP exception**"
        else:
            error_msg = "**an unknown error**"
        template = MuteResponseType.USER_FAIL

    banish_template = template_engine.get_template(ctx.invoked_with, template)
    if banish_template:
        reply = banish_template.substitute(
            author=author.mention,
            fails=fails,
            errors=error_msg,
            timestamp=duration
        )
        await ctx.send(reply)
    else:
        reply = "I couldn't find an appropriate response, but anyway... you're not "
        reply += f"allowed to do that! Bad {ctx.author.mention}!"
        await ctx.send(reply)
