import sys
import traceback

import inflect

from mrfreeze.bot import MrFreeze
from mrfreeze import colors

from .cogbase import CogBase

from discord.ext.commands import BadArgument, CheckFailure, CommandInvokeError
from discord.ext.commands import CommandNotFound, CommandOnCooldown
from discord.ext.commands.context import Context
from discord.ext.commands.cooldowns import BucketType

def setup(bot: MrFreeze):
    """Add the cog to the bot."""
    bot.add_cog(ErrorHandler(bot))


class ErrorHandler(CogBase):
    """How the bot acts when errors occur."""

    def __init__(self, bot: MrFreeze) -> None:
        self.bot = bot

    @CogBase.listener()
    async def on_command_error(self, ctx: Context, error) -> None:
        """What happens when we encounter a command error? This happens."""
        time: str = self.current_time()
        username: str = f"{ctx.author.name}#{ctx.author.discriminator}"
        mention: str = ctx.author.mention
        invocation: str = f"{colors.WHITE_B}{ctx.prefix}{ctx.invoked_with}"

        if isinstance(error, CheckFailure):
            print(f"{time} {colors.RED_B}Check failure: {colors.CYAN}" +
                  f"{username} tried to illegaly invoke {invocation}" +
                  f"{colors.RESET}")

        elif isinstance(error, BadArgument):
            print(f"{time} {colors.RED_B}Bad arguments: {colors.CYAN}{username} " +
                  f"while using command {invocation}{colors.RESET}")
            await ctx.send(f"{mention} That's not quite the information I " +
                           "need to execute that command.")

        elif isinstance(error, CommandNotFound):
            print(f"{time} {colors.RED_B}Command not found: {colors.CYAN}" +
                  f"{username} tried to use {invocation}{colors.RESET}")

        elif isinstance(error, CommandInvokeError):
            # On Timeout Error, a CommandInvokeError containing the original
            # error is returned. Not the original TimeoutError itself.
            error_name: str = type(error.original).__name__
            print(f"{time} {colors.RED_B}{error_name}: {colors.CYAN}" +
                  f"{username} tried to use {invocation}{colors.RESET}")

        elif isinstance(error, CommandOnCooldown):
            if error.cooldown.rate == 1:
                er_rate = "once"
            elif error.cooldown.rate == 2:
                er_rate = "twice"
            else:
                infl = inflect.engine()
                er_rate = infl.number_to_words(error.cooldown.rate) + ' times'

            er_per_sec = int(error.cooldown.per)
            er_retry_sec = int(error.retry_after)

            def seconds_parse(time_input):
                if time_input > 60:
                    input_min = int(time_input / 60)
                    input_sec = int(time_input - (input_min * 60))
                    if input_sec != 0:
                        return f"{input_min} min {input_sec} sec"
                    else:
                        return f"{input_min} min"
                else:
                    return f"{er_retry_sec} sec"

            er_per = seconds_parse(er_per_sec)
            er_retry = seconds_parse(er_retry_sec)

            bucket = error.cooldown.type
            if bucket == BucketType.user:
                er_type = " per user"
            elif bucket == BucketType.member:
                er_type = " per member"
            elif bucket == BucketType.guild:
                er_type = " per server"
            elif bucket == BucketType.channel:
                er_type = " per channel"
            # Coming in discord.py 1.3
            # elif bucket == BucketType.role:
            #     er_type = " per role"
            elif bucket == BucketType.category:
                er_type = " per channel category"
            else:
                er_type = ""

            await ctx.send(f"{mention} The command **{ctx.prefix}" +
                           f"{ctx.invoked_with}** can only be used " +
                           f"{er_rate} every {er_per}{er_type}." +
                           f"\nTry again in {er_retry}.")

        else:
            # Who knows what happened? The stack trace, that's who.
            print(f"{time} {colors.RED_B}Unclassified error: " +
                  f"{colors.WHITE_B}{error}{colors.RESET}")
            traceback.print_exception(
                    type(error),
                    error,
                    error.__traceback__,
                    file=sys.stderr
            )
