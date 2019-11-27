import inflect    # Used to convert number to word
import traceback  # Debugging
import sys        # Debugging
from internals.cogbase import CogBase

# Various errors that we're going to be testing for
from discord.ext.commands import CheckFailure, BadArgument, CommandInvokeError
from discord.ext.commands import CommandOnCooldown, CommandNotFound
from discord.ext.commands.cooldowns import BucketType

# Some imports used in type hints
from discord.ext.commands.context import Context
from internals.mrfreeze import MrFreeze


def setup(bot: MrFreeze):
    bot.add_cog(ErrorHandler(bot))


class ErrorHandler(CogBase):
    """
    How the bot acts when errors occur.
    """
    def __init__(self, bot: MrFreeze) -> None:
        self.bot = bot
        self.initialize_colors()

    @CogBase.listener()
    async def on_command_error(self, ctx: Context, error) -> None:
        """
        What happens when we encounter a command error? This happens.
        """
        time: str = self.current_time()
        username: str = f"{ctx.author.name}#{ctx.author.discriminator}"
        mention: str = ctx.author.mention
        invocation: str = f"{self.WHITE_B}{ctx.prefix}{ctx.invoked_with}"

        if isinstance(error, CheckFailure):
            print(f"{time} {self.RED_B}Check failure: {self.CYAN}" +
                  f"{username} tried to illegaly invoke {invocation}" +
                  f"{self.RESET}")

        elif isinstance(error, BadArgument):
            print(f"{time} {self.RED_B}Bad arguments: {self.CYAN}{username} " +
                  f"while using command {invocation}{self.RESET}")
            await ctx.send(f"{mention} That's not quite the information I " +
                           "need to execute that command.")

        elif isinstance(error, CommandNotFound):
            print(f"{time} {self.RED_B}Command not found: {self.CYAN}" +
                  f"{username} tried to use {invocation}{self.RESET}")

        elif isinstance(error, CommandInvokeError):
            # On Timeout Error, a CommandInvokeError containing the original
            # error is returned. Not the original TimeoutError itself.
            error_name: str = type(error.original).__name__
            print(f"{time} {self.RED_B}{error_name}: {self.CYAN}" +
                  f"{username} tried to use {invocation}{self.RESET}")

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
                er_type = " for every user"
            elif bucket == BucketType.member:
                er_type = " for every member"
            elif bucket == BucketType.guild:
                er_type = " in every server"
            elif bucket == BucketType.channel:
                er_type = " in every channel"
            else:
                er_type = ""

            await ctx.send(f"{mention} The command **{ctx.prefix}" +
                           f"{ctx.invoked_with}** can only be used " +
                           f"{er_rate} every {er_per}{er_type}." +
                           f"\nTry again in {er_retry}.")

        else:
            # Who knows what happened? The stack trace, that's who.
            print(f"{time} {self.RED_B}Unclassified error: " +
                  f"{self.WHITE_B}{error}{self.RESET}")
            traceback.print_exception(
                    type(error),
                    error,
                    error.__traceback__,
                    file=sys.stderr
            )
