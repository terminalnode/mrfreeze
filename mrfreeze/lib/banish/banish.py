"""Module for handling the banish command."""
import datetime
import logging
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

logger = logging.getLogger("BanishCommandModule")
forever_words = [
    "forever",
    "indefinite", "indefinitely",
    "eternity", "eternally"
]


async def run_command(
    ctx: Context,
    coginfo: CogInfo,
    template_engine: TemplateEngine,
    args: Tuple[str, ...]
) -> None:
    """Interpret the command and delegate task to the appropriate sub-function."""
    if template_engine.get_command_type(ctx.invoked_with) == MuteCommandType.UNDO:
        msg = await attempt_unbanish(ctx, coginfo, template_engine)
        await ctx.send(msg)
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
    owners_mentioned = [ u for u in ctx.message.mentions if await bot.is_owner(u) ]
    mentions = ctx.message.mentions
    mods = [ u for u in mentions if u.guild_permissions.administrator and u != bot.user ]
    users = [ u for u in mentions if not u.guild_permissions.administrator and u != bot.user ]

    if bot_mentioned or self_mentioned or mods or owners_mentioned:
        # Illegal banish, prepare silly response.
        if owners_mentioned:
            logger.debug("Setting template to MuteResponseType.FREEZE_OWNER")
            template = MuteResponseType.FREEZE_OWNER
            fails_list = owners_mentioned
        elif bot_mentioned and len(mentions) == 1:
            logger.debug("Setting template to MuteResponseType.FREEZE")
            template = MuteResponseType.FREEZE
            fails_list = [ bot.user ]
        elif bot_mentioned and self_mentioned and len(mentions) == 2:
            logger.debug("Setting template to MuteResponseType.FREEZE_SELF")
            template = MuteResponseType.FREEZE_SELF
            fails_list = [ bot.user, ctx.author ]
        elif bot_mentioned:
            logger.debug("Setting template to MuteResponseType.FREEZE_OTHERS")
            template = MuteResponseType.FREEZE_OTHERS
            fails_list = mods + users
        elif self_mentioned and len(mentions) == 1:
            logger.debug("Setting template to MuteResponseType.SELF")
            template = MuteResponseType.SELF
            fails_list = mods
        elif mods and len(mentions) == 1:
            logger.debug("Setting template to MuteResponseType.MOD")
            template = MuteResponseType.MOD
            fails_list = mods
        elif mods:
            logger.debug("Setting template to MuteResponseType.MODS")
            template = MuteResponseType.MODS
            fails_list = mods
        else:
            logger.warn("Setting template to MuteResponseType.INVALID")
            logger.warn(f"bot_mentioned={bot_mentioned}, self_mentioned={self_mentioned}")
            logger.warn(f"{len(mentions)} mentions={mentions}")
            logger.warn(f"{len(mods)} mods={mods}")
            logger.warn(f"{len(users)} users={users}")
            template = MuteResponseType.INVALID
            fails_list = mentions

        banish_template = template_engine.get_template(ctx.invoked_with, template)
        mention_fails = default.mentions_list(fails_list)
        if banish_template:
            msg = banish_template.substitute(author=ctx.author.mention, fails=mention_fails)
            await ctx.send(msg)

    else:
        # Legal banish, attempt banish.
        msg = await attempt_banish(ctx, coginfo, template_engine, users, args)
        await ctx.send(msg)


async def attempt_unbanish(
    ctx: Context,
    coginfo: CogInfo,
    template_engine: TemplateEngine
) -> str:
    """Undo one or more banishes."""
    if coginfo.bot:
        bot: MrFreeze = coginfo.bot

    mentions = ctx.message.mentions
    victims = [ u for u in mentions if not u.guild_permissions.administrator and u != bot.user ]
    success_list: List[Member] = list()
    fails_list: List[Member] = list()
    success_string = ""
    fails_string = ""
    error_string = ""
    http_exception = False
    forbidden_exception = False
    other_exception = False

    for victim in victims:
        error = await mute_db.carry_out_unbanish(bot, victim, logger)
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

    template = get_mute_response_type(success_list, fails_list, undo=True)
    logger.debug(f"attempt_banish(): Setting template to {template}")

    response_template = template_engine.get_template(ctx.invoked_with, template)
    if response_template:
        response = response_template.substitute(
            author=ctx.author.mention,
            victims=success_string,
            fails=fails_string,
            errors=error_string,
        )
        return f"{ctx.author.mention} {response}"
    else:
        return f"{ctx.author.mention} Something went wrong, I'm literally at a loss for words."


async def attempt_banish(
    ctx: Context,
    coginfo: CogInfo,
    template_engine: TemplateEngine,
    victims: List[Member],
    args: Tuple[str, ...]
) -> str:
    """Attempt to carry banish some people, then return an appropriate response."""
    if coginfo.bot:
        bot: MrFreeze = coginfo.bot

    success_list: List[Member] = list()
    fails_list: List[Member] = list()
    success_string = ""
    fails_string = ""
    error_string = ""
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

    template = get_mute_response_type(success_list, fails_list)
    logger.debug(f"attempt_banish(): Setting template to {template}")

    timestamp_template = template_engine.get_template(ctx.invoked_with, MuteResponseType.TIMESTAMP)
    if timestamp_template:
        timestamp = timestamp_template.substitute(duration=time.parse_timedelta(duration))
    else:
        logger.warn(f"template_engine.get_template({ctx.invoked_with}, TIMESTAMP) returned None!")
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


def get_mute_response_type(
    muted: List[Member],
    failed: List[Member],
    undo: bool = False
) -> MuteResponseType:
    """Get lists of successes and fails, return appropriate MuteResponseType."""
    successes   = len(muted)
    no_success  = (successes == 0)
    single      = (successes == 1)
    multi       = (successes > 1)
    failures    = len(failed)
    no_fails    = (failures == 0)
    fail        = (failures == 1)
    fails       = (failures > 1)

    if single and no_fails:
        return MuteResponseType.UNSINGLE if undo else MuteResponseType.SINGLE
    elif multi and no_fails:
        return MuteResponseType.UNMULTI if undo else MuteResponseType.MULTI
    elif fail and no_success:
        return MuteResponseType.UNFAIL if undo else MuteResponseType.FAIL
    elif fails and no_success:
        return MuteResponseType.UNFAILS if undo else MuteResponseType.FAILS
    elif single and fail:
        return MuteResponseType.UNSINGLE_FAIL if undo else MuteResponseType.SINGLE_FAIL
    elif single and fails:
        return MuteResponseType.UNSINGLE_FAILS if undo else MuteResponseType.SINGLE_FAILS
    elif multi and fail:
        return MuteResponseType.UNMULTI_FAIL if undo else MuteResponseType.MULTI_FAIL
    elif multi and fails:
        return MuteResponseType.UNMULTI_FAILS if undo else MuteResponseType.MULTI_FAILS

    return MuteResponseType.INVALID


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
        forever = any([ arg.lower() in forever_words for arg in args ])

        if not forever:
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
