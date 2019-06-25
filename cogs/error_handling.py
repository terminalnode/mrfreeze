import discord      # Required to check for a lot of different discord exceptions
import asyncio      # Required to check for asyncio.TimeoutErrors
import traceback    # Debugging
import sys          # Debugging

# If buckets are ever implemented again:
# from discord.ext.commands.cooldowns import BucketType
# import inflect
def setup(bot):
    bot.add_cog(ErrorHandlerCog(bot))

class ErrorHandlerCog(discord.ext.commands.Cog, name='ErrorHandler'):
    """How the bot acts when errors occur."""

    def __init__(self, bot):
        self.bot = bot

    @discord.ext.commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """What happens when we encounter a command error? This happens."""

        current_time = self.bot.current_time()
        userstr = f"{ctx.author.name}#{ctx.author.discriminator}"

        if isinstance(error, discord.ext.commands.CheckFailure):
            print(f"{current_time} {self.bot.RED_B}Check failure: {self.bot.CYAN}{userstr} tried to illegaly invoke {self.bot.WHITE_B}!{ctx.invoked_with}{self.bot.RESET}")

        elif isinstance(error, discord.ext.commands.errors.BadArgument):
            print(f"{current_time} {self.bot.RED_B}Bad arguments: {userstr} while using command {self.bot.WHITE_B}!{ctx.invoked_with}{self.bot.RESET}")
            await ctx.send(f"{ctx.author.mention} That's not quite the information I need to execute that command.")

        elif isinstance(error, discord.ext.commands.errors.CommandNotFound):
            print(f"{current_time} {self.bot.RED_B}Command not found: {self.bot.CYAN}{userstr} tried {self.bot.WHITE_B}!{ctx.invoked_with}{self.bot.RESET}")

        elif isinstance(error, asyncio.TimeoutError):
            print(f"{current_time} {self.bot.RED_B}AsyncIO Timeout {self.bot.RESET}")

        elif isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
            if error.cooldown.rate == 1:    er_rate = 'once'
            elif error.cooldown.rate == 2:  er_rate = 'twice'
            else:
                infl    = inflect.engine()
                er_rate = infl.number_to_words(error.cooldown.rate) + ' times'

            er_per_sec   = int(error.cooldown.per)
            er_retry_sec = int(error.retry_after)

            def seconds_parse(time_input):
                if time_input > 60:
                    input_min = int(time_input / 60)
                    input_sec = int(time_input - (input_min * 60))
                    if input_sec != 0:  return f"{input_min} min {input_sec} sec"
                    else:               return f"{input_min} min"
                else:                   return f"{input_sec} sec"

            er_per = seconds_parse(er_per_sec)
            er_retry = seconds_parse(er_retry_sec)

            bucket = error.cooldown.type
            if bucket == BucketType.default:    er_type = '' # Writing nothing is fine here.
            elif bucket == BucketType.user:     er_type = ' by every user'
            elif bucket == BucketType.guild:    er_type = ' in every server'
            elif bucket == BucketType.channel:  er_type = ' in every channel'
            elif bucket == BucketType.member:   er_type = ' by every user'
            else:                               er_type = ' [missing bucket type]'

            await ctx.send("{ctx.author.name} The command **{ctx.invoked_with}** can only be used {er_rate} every {er_per}{er_type}. Try again in {er_retry}.")

        else:
            print(f"{current_time} {self.bot.RED_B}Unclassified error: {self.bot.WHITE_B}{error}{self.bot.RESET}")
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
