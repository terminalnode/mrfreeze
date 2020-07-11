"""Module for methods used by the error handling cog."""

import sys
import traceback
from logging import Logger

from discord.ext.commands import BadArgument
from discord.ext.commands import CheckFailure
from discord.ext.commands import CommandInvokeError
from discord.ext.commands import CommandNotFound
from discord.ext.commands import CommandOnCooldown
from discord.ext.commands import Context
from discord.ext.commands import MissingRequiredArgument
from discord.ext.commands.cooldowns import BucketType

import inflect

from mrfreeze.lib.checks import MuteCheckFailure
from mrfreeze.lib.colors import CYAN
from mrfreeze.lib.colors import CYAN_B
from mrfreeze.lib.colors import MAGENTA
from mrfreeze.lib.colors import RED_B
from mrfreeze.lib.colors import RESET
from mrfreeze.lib.colors import WHITE_B
from mrfreeze.lib.colors import YELLOW


class ContextData:
    """Class for holding contextual information."""

    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx
        self.user: str = f"{ctx.author.name}#{ctx.author.discriminator}"
        self.member: str = f"{YELLOW}{ctx.author} {CYAN_B}@ {MAGENTA}{ctx.guild.name}"
        self.mention: str = ctx.author.mention
        self.plain_invocation: str = f"{ctx.prefix}{ctx.invoked_with}"
        self.invocation: str = f"{WHITE_B}{self.plain_invocation}{RESET}"


def color_error(name: str) -> str:
    """Return the name of the error in color for consistency throughout all errors."""
    return f"{RED_B}{name}: {CYAN}"


async def test_everything(ctx: Context, error: Exception, logger: Logger) -> None:
    """Method for running all of the tests in sequence."""
    test_sequence = [
        test_mute_check_failure, test_check_failure, test_missing_argument,
        test_bad_argument, test_command_not_found, test_command_invoke_error,
        test_command_on_cooldown
    ]

    for test in test_sequence:
        if await test(ctx, error, logger):
            return

    # Who knows what happened? The stack trace, that's who.
    name = color_error("Unclassified error")
    status = f"{name}{WHITE_B}{error}{RESET}"
    logger.error(status)
    traceback.print_exception(
        type(error),
        error,
        error.__traceback__,
        file=sys.stderr
    )


async def test_mute_check_failure(ctx: Context, error: Exception, logger: Logger) -> bool:
    """Test if the error is a MuteCheckFailure."""
    if isinstance(error, MuteCheckFailure):
        cd = ContextData(ctx)
        name = color_error("Freeze muted")
        status  = f"{name}{cd.member} {cd.invocation}{RESET}"
        logger.error(status)
        return True

    return False


async def test_check_failure(ctx: Context, error: Exception, logger: Logger) -> bool:
    """Test if the error is a CheckFailure."""
    if isinstance(error, CheckFailure):
        cd = ContextData(ctx)
        name = color_error("Check failure")
        status = f"{name}{cd.member} tried to illegaly invoke {cd.invocation}{RESET}"
        logger.error(status)
        return True

    return False


async def test_missing_argument(ctx: Context, error: Exception, logger: Logger) -> bool:
    """Test if the error is a MissingArgument."""
    if isinstance(error, MissingRequiredArgument):
        cd = ContextData(ctx)
        name = color_error("Missing argument")

        status = f"{name}{cd.member} tried executing {cd.invocation} with too few arguments{RESET}"
        logger.error(status)

        reply  = f"{cd.mention} You need to specify some arguments to invoke "
        reply += f"{cd.plain_invocation}, or I won't know what to do."
        await ctx.send(reply)
        return True

    return False


async def test_bad_argument(ctx: Context, error: Exception, logger: Logger) -> bool:
    """Test if the error is a BadArgument."""
    if isinstance(error, BadArgument):
        cd = ContextData(ctx)
        name = color_error("Bad argument")

        status = f"{name}{cd.member} while using command {cd.invocation}{RESET}"
        logger.error(status)
        logger.error(error)

        reply = f"{cd.mention} That's not quite the information I need to execute that command."
        await ctx.send(reply)
        return True

    return False


async def test_command_not_found(ctx: Context, error: Exception, logger: Logger) -> bool:
    """Test if the error is a CommandNotFound."""
    if isinstance(error, CommandNotFound):
        cd = ContextData(ctx)
        name = color_error("Command not found")

        status = f"{name}{cd.member} tried to use {cd.invocation}{RESET}"
        logger.error(status)
        return True

    return False


async def test_command_invoke_error(ctx: Context, error: Exception, logger: Logger) -> bool:
    """Test if the error is a CommandInvokeError."""
    if isinstance(error, CommandInvokeError):
        cd = ContextData(ctx)
        error_name: str = type(error.original).__name__
        name = color_error(error_name)

        status = f"{name}{cd.member} tried to use {cd.invocation}{RESET}"
        logger.error(status)
        return True

    return False


async def test_command_on_cooldown(ctx: Context, error: Exception, logger: Logger) -> bool:
    """Test if the error is a CommandOnCooldown."""
    if isinstance(error, CommandOnCooldown):
        cd = ContextData(ctx)
        name = color_error("Command on cooldown")

        if error.cooldown.rate == 1:
            rate = "once"
        elif error.cooldown.rate == 2:
            rate = "twice"
        else:
            infl = inflect.engine()
            rate = f"{infl.number_to_words(error.cooldown.rate)} times"

        per = seconds_parse(error.cooldown.per)
        retry_after = seconds_parse(round(error.retry_after))

        bucket_type = bucket_to_string(error)

        status = f"{name}{cd.member} while using {cd.invocation}"
        logger.error(status)

        msg  = f"{cd.mention} The command **{ctx.prefix}{ctx.invoked_with}** can only be used "
        msg += f"{rate} every {per}{bucket_type}.\nTry again in {retry_after}."
        await ctx.send(msg)

        return True

    return False


def seconds_parse(num_seconds: int) -> str:
    """Convert an integer number of seconds to a x min y sec-style string."""
    if num_seconds > 60:
        input_min = int(num_seconds / 60)
        input_sec = int(num_seconds - (input_min * 60))

        if input_sec != 0:
            return f"{input_min} min {input_sec} sec"
        else:
            return f"{input_min} min"

    else:
        return f"{num_seconds} sec"


def bucket_to_string(error: CommandOnCooldown) -> str:
    """Convert CommandOnCooldown BucketType to text."""
    type = error.cooldown.type
    string: str = ""

    if type == BucketType.user:
        string = " per user"

    elif type == BucketType.member:
        string = " per member"

    elif type == BucketType.guild:
        string = " per server"

    elif type == BucketType.channel:
        string = " per channel"

    elif type == BucketType.role:
        string = " per role"

    elif type == BucketType.category:
        string = " per channel category"

    return string
