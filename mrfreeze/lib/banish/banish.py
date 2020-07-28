"""Module for handling the banish command."""
import datetime
from logging import Logger
from typing import List
from typing import Optional
from typing import Tuple

import discord
from discord import Member
from discord.ext.commands import Context

from mrfreeze.bot import MrFreeze
from mrfreeze.cogs.coginfo import CogInfo
from mrfreeze.cogs.coginfo import InsufficientCogInfo
from mrfreeze.lib import default
from mrfreeze.lib import time
from mrfreeze.lib.banish import mute_db
from mrfreeze.lib.banish.templates import MuteCommandType
from mrfreeze.lib.banish.templates import MuteResponseType
from mrfreeze.lib.banish.templates import TemplateEngine


async def run_command(
    ctx: Context,
    coginfo: CogInfo,
    template_engine: TemplateEngine,
    args: Tuple[str, ...]
) -> None:
    """Interpret the command and delegate task to the appropriate sub-function."""
    if template_engine.get_command_type(ctx.invoked_with) == MuteCommandType.UNDO:
        await unbanish(ctx, coginfo, template_engine)
    else:
        await banish(ctx, coginfo, template_engine, args)


async def banish(
    ctx: Context,
    coginfo: CogInfo,
    template_engine: TemplateEngine,
    args: Tuple[str, ...]
) -> None:
    """Carry out one or more banishes."""
    if coginfo.bot:
        bot: MrFreeze = coginfo.bot
    else:
        raise InsufficientCogInfo()

    # Parse targetted users
    bot_mentioned = bot.user in ctx.message.mentions
    self_mentioned = ctx.author in ctx.message.mentions
    mentions = [ u for u in ctx.message.mentions if u != bot.user ]
    target_mods = [ u for u in mentions if u.guild_permissions.administrator ]
    target_users = [ u for u in mentions if not u.guild_permissions.administrator ]

    if bot_mentioned or self_mentioned or target_mods:
        # Illegal banish, prepare silly response.
        pass

    else:
        # Legal banish, attempt banish.
        msg = await attempt_banish(ctx, coginfo, template_engine, target_users, args)
        await ctx.send(msg)


async def attempt_banish(
    ctx: Context,
    coginfo: CogInfo,
    template_engine: TemplateEngine,
    victims: List[Member],
    args: Tuple[str, ...]
) -> str:
    """Attempt to carry banish some people, then return an appropriate response."""
    if coginfo.bot and coginfo.logger:
        bot: MrFreeze = coginfo.bot
        logger: Logger = coginfo.logger

    success_list: List[Member] = list()
    fails_list: List[Member] = list()
    http_exception = False
    forbidden_exception = False
    other_exception = False
    duration, end_date = get_unbanish_duration(ctx, template_engine, args)

    for victim in victims:
        error = await mute_db.carry_out_banish(bot, victim, logger, end_date)
        if isinstance(error, Exception):
            fails_list.append(victim)
            if isinstance(error, discord.HTTPException):
                http_exception = True
            elif isinstance(error, discord.Forbidden):
                forbidden_exception = True
            else:
                other_exception = True

        else:
            success_list.append(victim)

        success_string = default.mentions_list(success_list)
        fails_string = default.mentions_list(fails_list)
        error_string = get_error_string(http_exception, forbidden_exception, other_exception)

    successes   = len(success_list)
    no_success  = (successes == 0)
    single      = (successes == 1)
    multi       = (successes > 1)
    failures    = len(fails_list)
    no_fails    = (failures == 0)
    fail        = (failures == 1)
    fails       = (failures > 1)

    if single and no_fails:
        template = MuteResponseType.SINGLE
    elif multi and no_fails:
        template = MuteResponseType.MULTI
    elif fail and no_success:
        template = MuteResponseType.FAIL
    elif fails and no_success:
        template = MuteResponseType.FAILS
    elif single and fail:
        template = MuteResponseType.SINGLE_FAIL
    elif single and fails:
        template = MuteResponseType.SINGLE_FAILS
    elif multi and fail:
        template = MuteResponseType.MULTI_FAIL
    elif multi and fails:
        template = MuteResponseType.MULTI_FAILS
    else:
        template = MuteResponseType.INVALID

    timestamp_template = template_engine.get_template(ctx.invoked_with, MuteResponseType.TIMESTAMP)
    if timestamp_template:
        timestamp = timestamp_template.substitute(duration=time.parse_timedelta(duration))
    else:
        timestamp = ""

    response_template = template_engine.get_template(ctx.invoked_with, template)
    if response_template:
        response = response_template.substitute(
            author=ctx.author.mention,
            victims=success_string,
            fails=fails_string,
            errors=error_string,
            timestamp=timestamp
        )
        return f"{ctx.author.mention} {response}"
    else:
        return f"{ctx.author.mention} Something went wrong, I'm literally at a loss for words."


def get_error_string(http: bool, forbidden: bool, other: bool) -> str:
    """Take occurences of errors as booleans, return a string describing the problem."""
    if http and forbidden and other:
        return "**a wild mix of crazy exceptions**"
    elif http and forbidden:
        return "**a mix of HTTP exception and lack of privilegies**"
    elif http and other:
        return "**a wild mix of HTTP exception and other stuff**"
    elif forbidden and other:
        return "**a wild mix of lacking privilegies and some other stuff**"
    elif http:
        return "**an HTTP exception**"
    elif forbidden:
        return "**a lack of privilegies**"
    else:
        return "**an unidentified exception**"


def get_unbanish_duration(
    ctx: Context,
    template_engine: TemplateEngine,
    args: Tuple[str, ...]
) -> Tuple[Optional[datetime.timedelta], Optional[datetime.datetime]]:
    """Return appropriate duration and end date for a banish."""
    duration, end_date = time.extract_time(args)

    if duration is None:
        command_type = template_engine.get_command_type(ctx.invoked_with)
        current_time = datetime.datetime.now()

        try:
            if command_type == MuteCommandType.MICRO:
                duration = datetime.timedelta(seconds=10)
            elif command_type == MuteCommandType.SUPER:
                duration = datetime.timedelta(weeks=1)
            elif command_type == MuteCommandType.MEGA:
                duration = datetime.timedelta(days=365)
            else:
                duration = datetime.timedelta(minutes=5)

            end_date = current_time + duration

        except OverflowError:
            end_date = datetime.datetime.max
            duration = end_date - current_time

    return duration, end_date


async def unbanish(ctx: Context, coginfo: CogInfo, template_engine: TemplateEngine) -> None:
    """Undo one or more banishes."""
    if coginfo.logger:
        coginfo.logger.info("Hello, this is unbanish method. I'm not done yet.")
    await ctx.send("Unbanish is not done yet, thanks for flying with MrFreeze Airlines.")
