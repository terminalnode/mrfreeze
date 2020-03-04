"""
Banish cog.

This cog is for the banish/mute command and the region command.
banish/mute is closely connected to the region command since
they both use the antarctica mechanics.

Therefor they're both in a cog separate from everything else.
"""

import asyncio
import datetime
import random
from typing import Iterable

import discord
from discord import Guild

from mrfreeze import checks
from mrfreeze import colors
from mrfreeze.bot import MrFreeze
from mrfreeze.cogs.cogbase import CogBase

from mrfreeze.cogs.banish.enums import MuteType, MuteStr
from mrfreeze.cogs.banish.templates import templates
from mrfreeze.cogs.banish import mute_db, region_db


banish_aliases = ["unbanish", "microbanish",
                  "superbanish", "SUPERBANISH",
                  "megabanish", "MEGABANISH"]

hogtie_aliases = ["hogtie", "unhogtie", "microhogtie",
                  "tie", "untie", "microtie",
                  "superhogtie", "SUPERHOGTIE",
                  "supertie", "SUPERTIE",
                  "megahogtie", "MEGAHOGTIE",
                  "megatie", "MEGATIE"]

mute_aliases = ["mute", "unmute", "micromute",
                "supermute", "SUPERMUTE",
                "megamute", "MEGAMUTE"]

all_aliases = banish_aliases + hogtie_aliases + mute_aliases


def setup(bot: MrFreeze) -> None:
    """Load the cog into the bot."""
    bot.add_cog(BanishAndRegion(bot))


class BanishAndRegion(CogBase):
    """Good mod! Read the manual! Or if you're not mod - sod off!"""

    def __init__(self, bot: MrFreeze, mdbname: str = "mutes", rdbname: str = "regions") -> None:
        self.bot = bot

        # Server setting names
        # Mute interval governs how often to check for unmutes.
        self.mute_interval_name = 'mute_interval'
        self.default_mute_interval = 5
        self.mute_interval_dict = dict()

        # Self mute interval governs how long to banish
        # unauthorized uses of !mute/!banish etc
        self.self_mute_time_name = 'self_mute_time'
        self.default_self_mute_time = 20
        self.self_mute_time_dict = dict()

        # Mutes database creation
        self.mdbname = mdbname
        mdbtable = f"""CREATE TABLE IF NOT EXISTS {self.mdbname}(
            id          integer NOT NULL,
            server      integer NOT NULL,
            voluntary   boolean NOT NULL,
            until       date,
            CONSTRAINT  server_user PRIMARY KEY (id, server));"""
        bot.db_create(self.bot, self.mdbname, mdbtable)

        # Region database creation
        self.rdbname = rdbname
        self.region_table = "region"
        self.blacklist_table = "blacklist"
        # Complete list of tables and their rows in this database.
        # Primary key(s) is marked with an asterisk (*).
        # Mandatory but not primary keys are marked with a pling (!).
        # TABLE                 ROWS       TYPE     FUNCTION
        # self.region_table     role*      integer  Role ID
        #                       server*    integer  Server ID
        #                       triggers!  string   String of keywords for region
        # self.blacklist_table  uid*       integer  User ID
        #                       sid*       integer  Server ID
        rdbtable = f"""CREATE TABLE IF NOT EXISTS {self.region_table}(
            role        integer NOT NULL,
            server      integer NOT NULL,
            triggers    str NOT NULL,
            CONSTRAINT  server_user PRIMARY KEY (role, server));"""

        rdbtable_bl = f"""CREATE TABLE IF NOT EXISTS {self.blacklist_table}(
            uid         integer NOT NULL,
            sid         integer NOT NULL,
            CONSTRAINT  sid_uid PRIMARY KEY (uid, sid));"""

        bot.db_create(self.bot, self.rdbname, rdbtable, comment="region table")
        bot.db_create(self.bot, self.rdbname, rdbtable_bl, comment="blacklist table")

    def word_distance(self, a: str, b: str) -> int:
        """Get the word distance between two words."""
        arr = [ [ 0 for x in range(len(b)) ] for y in range(len(a)) ]
        for x in range(0, len(a)):
            arr[x][0] = x
        for x in range(0, len(b)):
            arr[0][x] = x
        for row in range(1, len(a)):
            for col in range(1, len(b)):
                if a[row] == b[col]:
                    cost = 0
                else:
                    cost = 1
        arr[row][col] = min(
            1 + arr[row - 1][col],
            1 + arr[row][col - 1],
            cost + arr[row - 1][col - 1])

        return arr[len(a) - 1][len(b) - 1]

    def get_closest_match(self, candidates: Iterable[str], input: str) -> str:
        """
        Get the closest matching string from a list of candidates.

        This method acts as a wrapper for word distance.
        """
        return min(candidates, key=lambda k: self.word_distance(k, input))

    @CogBase.listener()
    async def on_ready(self):
        for server in self.bot.guilds:
            # Set intervals in which to check mutes
            mute_interval = self.bot.read_server_setting(self.bot, server, self.mute_interval_name)
            if mute_interval and mute_interval.isdigit():
                self.mute_interval_dict[server.id] = int(mute_interval)
            else:
                self.mute_interval_dict[server.id] = self.default_mute_interval

            # Add unbanish loop to bot
            self.bot.add_bg_task(self.unbanish_loop(server), f'unbanish@{server.id}')

            # Set how long a member should be punished for after unauthorized !mute usage
            self_mute_time = self.bot.read_server_setting(self.bot, server, self.self_mute_time_name)
            if self_mute_time and self_mute_time.isdigit():
                self.self_mute_time_dict[server.id] = int(self_mute_time)
            else:
                self.self_mute_time_dict[server.id] = self.default_self_mute_time

    async def unbanish_loop(self, server: Guild) -> None:
        """Check for people to unbanish every self.banish_interval seconds."""
        while not self.bot.is_closed():
            await asyncio.sleep(self.mute_interval_dict[server.id])

            current_time = datetime.datetime.now()
            server_mutes = mute_db.mdb_fetch(self.bot, self.mdbname, server)
            mute_role = await self.bot.get_mute_role(server)
            mute_channel = await self.bot.get_mute_channel(server)
            unmuted = list()

            for mute in server_mutes:
                if mute.until is None:
                    continue

                member = mute.member
                until = mute.until

                if until < current_time:
                    diff = self.bot.parse_timedelta(current_time - until)
                    if diff == "":
                        diff = "now"
                    else:
                        diff = f"{diff} ago"

                    mute_db.mdb_del(self.bot, self.mdbname, member) # Remove from database
                    if mute_role in member.roles:
                        try:
                            await member.remove_roles(mute_role)
                            # Members are only considered unmuted if they had the antarctica role
                            unmuted.append(member)
                        except Exception as e:
                            print(f"{self.current_time()} {colors.RED_B}Mutes DB:{colors.CYAN} failed to remove " +
                                f"mute role of{colors.CYAN_B} {member.name}#{member.discriminator} @ {server.name}.\n" +
                                f"{colors.RED}==> {e}{colors.RESET}")

                    print(f"{self.current_time()} {colors.GREEN_B}Mutes DB:{colors.CYAN} auto-unmuted " +
                        f"{colors.CYAN_B}{member.name}#{member.discriminator} @ {server.name}." +
                        f"{colors.YELLOW} (due {diff}){colors.RESET}")

            # Time for some great regrets
            if len(unmuted) > 0:
                unmuted = self.mentions_list(unmuted)
                if len(unmuted) == 1:
                    await mute_channel.send(
                        f"It's with great regret that I must inform you all that {unmuted}'s exile has come to an end."
                    )
                else:
                    await mute_channel.send(
                        f"It's with great regret that I must inform you all that the exile of {unmuted} has come to an end."
                    )

    @discord.ext.commands.command(name='banishinterval', aliases=['banishint', 'baninterval', 'banint', 'muteinterval', 'muteint'])
    @discord.ext.commands.check(checks.is_mod)
    async def _banishinterval(self, ctx, *args):
        author = ctx.author.mention
        server = ctx.guild
        interval = None

        # Look for first number in args and use as interval time.
        for arg in args:
            if arg.isdigit():
                interval = int(arg)
                break

        if interval is None:
            await ctx.send(f"{author} You didn't specify a valid interval. Please try again.")

        elif interval == self.mute_interval_dict[server.id]:
            await ctx.send(f"{author} The interval for this server is already set to {interval}.")

        elif interval < 5:
            await ctx.send(f"{author} You greedy little smud you, trying to steal my CPU cycles like that. Minimum interval is 5 seconds.")

        else:
            oldinterval = self.mute_interval_dict[server.id]
            self.mute_interval_dict[server.id] = interval
            setting_saved = self.bot.write_server_setting(self.bot, server, self.mute_interval_name, str(interval))
            if setting_saved:
                await ctx.send(f"{author} The interval has been changed from {oldinterval} to {interval} seconds.")
            else:
                await ctx.send(f"{author} The interval has been changed from {oldinterval} to {interval} seconds, *BUT* " +
                    f"for some reason I was unable to save this setting, so it will be reset to {oldinterval} once I restart.")

    @discord.ext.commands.command(name='selfmutetime', aliases=['smt', 'selfmute', 'mutetime'])
    @discord.ext.commands.check(checks.is_mod)
    async def _selfmutetime(self, ctx, *args):
        author = ctx.author.mention
        server = ctx.guild
        proposed_time = None

        # Look for first number in args and use as new self mute time.
        for arg in args:
            if arg.isdigit():
                proposed_time = int(arg)
                break

        if proposed_time is None:
            await ctx.send(f"{author} Please specify the time in minutes and try again.")

        elif proposed_time == self.self_mute_time_dict[server.id]:
            await ctx.send(f"{author} The self mute time for this server is already set to {proposed_time}.")

        elif proposed_time == 0:
            await ctx.send(f"{author} Zero is not a valid self mute time, smud.")

        elif proposed_time > 3600 * 24 * 7:
            await ctx.send(f"{author} I may be evil, but even I think more than a weeks punishment is a bit harsh...")

        else:
            old_time = self.self_mute_time_dict[server.id]
            self.self_mute_time_dict[server.id] = proposed_time
            setting_saved = self.bot.write_server_setting(self.bot, server, self.self_mute_time_name, str(proposed_time))
            if setting_saved:
                await ctx.send(f"{author} The self mute time has been changed from {old_time} to {proposed_time} minutes.")
            else:
                await ctx.send(f"{author} The self mute time has been changed from {old_time} to {proposed_time} minutes, *BUT* " +
                        f"for some reason I was unable to save this setting, so it will be reset to {old_time} once I restart.")

    @discord.ext.commands.command(name='banish', aliases=all_aliases)
    @discord.ext.commands.check(checks.is_mod)
    async def _banish(self, ctx, *args):
        """Mute one or more users (can only be invoked by mods)"""
        # Lists where we will store our results
        success_list = list()
        fails_list = list()

        # Variables checking for specific exceptions
        http_exception = False
        forbidden_exception = False
        other_exception = False

        # Message parsing
        mentions = ctx.message.mentions
        bot = self.bot.user in mentions
        slf = ctx.author in mentions
        mod = [ user for user in mentions if await checks.is_mod(user) and user != self.bot.user ]
        usr = [ user for user in mentions if user not in mod and user != self.bot.user ]

        invocation = ctx.invoked_with.lower()
        if invocation[:2] == "un":  unmute = True
        else:                       unmute = False

        is_super = 'super' in invocation
        is_mega = 'mega' in invocation

        if invocation == "banish":          invocation = MuteType.BANISH
        elif invocation in banish_aliases:  invocation = MuteType.BANISH
        elif invocation in hogtie_aliases:  invocation = MuteType.HOGTIE
        elif invocation in mute_aliases:    invocation = MuteType.MUTE

        # Extract durations from statement
        # If no time is stated both of these will be None
        duration, end_date = self.bot.extract_time(args)

        # Add time if invocation is super or mega
        if is_super or is_mega:
            # Make sure a timedelta exists first.
            if duration is None:
                duration = datetime.timedelta()

            # Super adds a week, mega adds a year
            # (or 365 days because timedelta doesn't support years)
            current_time = datetime.datetime.now()
            try:
                if is_super:    duration += datetime.timedelta(weeks=1)
                elif is_mega:   duration += datetime.timedelta(days=365)
                end_date = current_time + duration
            except OverflowError:
                end_date = datetime.datetime.max
                duration = end_date - current_time

        if len(mentions) == 0:
            template = MuteStr.NONE

        elif bot and not unmute:
            # Freeze mutes: FREEZE, FREEZE_SELF, FREEZE_OTHERS
            if len(mentions) == 1:              template = MuteStr.FREEZE
            elif len(mentions) == 2 and slf:    template = MuteStr.FREEZE_SELF
            else:                               template = MuteStr.FREEZE_OTHERS
            fails_list = usr + mod

        elif mod and not unmute:
            # Mod mutes: SELF, MOD, MODS
            if len(mentions) == 1 and slf:      template = MuteStr.SELF
            elif len(mentions) == 1:            template = MuteStr.MOD
            else:                               template = MuteStr.MODS
            fails_list = mod

        else:
            # Working mutes (at user mutes):
            # SINGLE, MULTI, FAIL, FAILS, SINGLE_FAIL, SINGLE_FAILS, MULTI_FAIL, MULTI_FAILS
            for member in usr:
                if unmute:
                    error = await mute_db.carry_out_unbanish(self.bot, self.mdbname, member)
                else:
                    error = await mute_db.carry_out_banish(self.bot, self.mdbname, member, end_date)

                if isinstance(error, Exception):
                    fails_list.append(member)
                    if isinstance(error, discord.HTTPException):    http_exception = True
                    elif isinstance(error, discord.Forbidden):      forbidden_exception = True
                    else:                                           other_exception = True

                else:
                    success_list.append(member)

            if not usr and unmute:
                # Fully invalid unbanish attempt!
                template = MuteStr.INVALID

            successes   = len(success_list)
            no_success  = (successes == 0)
            single      = (successes == 1)
            multi       = (successes > 1)
            failures    = len(fails_list)
            no_fails    = (failures == 0)
            fail        = (failures == 1)
            fails       = (failures > 1)

            if single and no_fails and unmute:      template = MuteStr.UNSINGLE
            elif single and no_fails:               template = MuteStr.SINGLE
            elif multi and no_fails and unmute:     template = MuteStr.UNMULTI
            elif multi and no_fails:                template = MuteStr.MULTI
            elif fail and no_success and unmute:    template = MuteStr.UNFAIL
            elif fail and no_success:               template = MuteStr.FAIL
            elif fails and no_success and unmute:   template = MuteStr.UNFAILS
            elif fails and no_success:              template = MuteStr.FAILS
            elif single and fail and unmute:        template = MuteStr.UNSINGLE_FAIL
            elif single and fail:                   template = MuteStr.SINGLE_FAIL
            elif single and fails and unmute:       template = MuteStr.UNSINGLE_FAILS
            elif single and fails:                  template = MuteStr.SINGLE_FAILS
            elif multi and fail and unmute:         template = MuteStr.UNMULTI_FAIL
            elif multi and fail:                    template = MuteStr.MULTI_FAIL
            elif multi and fails and unmute:        template = MuteStr.UNMULTI_FAILS
            elif multi and fails:                   template = MuteStr.MULTI_FAILS

        # TESTING THINGIE - leave commented unless testing
        # fails_list = success_list
        # template = MuteStr.FAIL
        # template = MuteStr.FAILS
        # template = MuteStr.SINGLE_FAIL
        # template = MuteStr.SINGLE_FAILS
        # template = MuteStr.MULTI_FAIL
        # template = MuteStr.MULTI_FAILS
        # template = MuteStr.MULTI_FAIL
        # template = MuteStr.UNFAIL
        # template = MuteStr.UNFAILS
        # template = MuteStr.UNSINGLE_FAIL
        # template = MuteStr.UNSINGLE_FAILS
        # template = MuteStr.UNMULTI_FAIL
        # template = MuteStr.UNMULTI_FAILS
        # http_exception = True
        # forbidden_exception = True
        # other_exception = True

        # Turn successes, fails and exceptions into strings
        success_list = self.mentions_list(success_list)
        fails_list = self.mentions_list(fails_list)
        error = str()

        if http_exception and forbidden_exception and other_exception:  error = "**a wild mix of crazy exceptions**"
        elif http_exception and forbidden_exception:                    error = "**a mix of HTTP exception and lack of privilegies**"
        elif http_exception and other_exception:                        error = "**a wild mix of HTTP exception and other stuff**"
        elif forbidden_exception and other_exception:                   error = "**a wild mix of lacking privilegies and some other stuff**"
        elif http_exception:                                            error = "**an HTTP exception**"
        elif forbidden_exception:                                       error = "**a lack of privilegies**"
        else:                                                           error = "**an unidentified exception**"

        # Create string
        timestamp = templates[invocation][MuteStr.TIMESTAMP].substitute(
               duration=self.bot.parse_timedelta(duration)
        )

        reply =f"{ctx.author.mention} " + templates[invocation][template].substitute(
            author=ctx.author.mention, victims=success_list, fails=fails_list, errors=error, timestamp=timestamp
        )
        await ctx.send(reply)

    # This decorator makes it discord.py automatically
    # trigger it when _banish throws an error.
    @_banish.error
    async def unauthorized_banish(self, ctx, error):
        """
        Trigger on unauthorized banish, i.e. when a non-administrator try to banish one or more people.

        When _banish() encounters an error this method is automatically triggered. If the error
        is an instance of discord.ext.commands.CheckFailure the user will be punished accordingly,
        if not the error is raised again.

        There are four relevant templates that can be used when sending the response.
        USER_NONE     User invoked mute with no arguments
        USER_SELF     User tried muting themselves
        USER_USER     User tried muting other user(s)
        USER_MIXED    User tried musing themselves and other user(s)
        """

        if not isinstance(error, discord.ext.commands.CheckFailure):
            # Only run this on Check Failure.
            return
        else:
            raise error

        mentions = ctx.message.mentions
        author = ctx.author
        server = ctx.guild

        invocation = ctx.invoked_with
        if invocation == "banish":          invocation = MuteType.BANISH
        elif invocation in banish_aliases:  invocation = MuteType.BANISH
        elif invocation in hogtie_aliases:  invocation = MuteType.HOGTIE
        elif invocation in mute_aliases:    invocation = MuteType.MUTE

        none     = (len(mentions) == 0)
        selfmute = (len(mentions) == 1 and author in mentions)
        mix      = (not selfmute and author in mentions)
        user     = (not selfmute and not mix and len(mentions) > 0)
        fails    = self.mentions_list([ mention for mention in mentions if mention != author ])

        if none:        template = MuteStr.USER_NONE
        elif selfmute:  template = MuteStr.USER_SELF
        elif user:      template = MuteStr.USER_USER
        elif mix:       template = MuteStr.USER_MIXED

        duration = datetime.timedelta(minutes = self.self_mute_time_dict[server.id])
        end_date = datetime.datetime.now() + duration
        duration = self.bot.parse_timedelta(duration)

        # Carry out the banish with resulting end date
        error = await mute_db.carry_out_banish(self.bot, self.mdbname, author, end_date)

        if isinstance(error, Exception):
            if isinstance(error, discord.Forbidden):        error = "**a lack of privilegies**"
            elif isinstance(error, discord.HTTPException):  error = "**an HTTP exception**"
            else:                                           error = "**an unknown error**"
            template = MuteStr.USER_FAIL

        reply=templates[invocation][template].substitute(
            author=author.mention, fails=fails, errors=error, timestamp=duration
        )

        await ctx.send(reply)

    @discord.ext.commands.command(name="roulette")
    async def roulette(self, ctx, *args):
        member = ctx.author
        mention = member.mention
        http_exception = False
        forbidden_exception = False
        other_exception = False

        # Skip if server is Penposium and channel isn't #bot-trash or #bots
        if ctx.guild.id == 444289793141112864 and ctx.channel.id not in (471909336377982976, 445708393789915146):
            await ctx.send("Please only use that command in the bot-trash channel... smud.")
            return

        if random.randint(1, 6) == 1:
            # Tough luck, yer goin' down

            banish_time = random.randint(1, 5)
            duration = datetime.timedelta(minutes = banish_time)
            end_date = datetime.datetime.now() + duration
            reply = "I should probably say something now... but I don't know what."

            if banish_time == 1:
                reply = f"{mention} rolls the dice, the gun doesn't fire but somehow "
                reply += "they manage to hurt themselves with it anyway. A minute in "
                reply += "Antarctica and they'll be good as new!"

            elif banish_time == 2:
                reply = f"{mention} rolls the dice, but the gun misfires and explodes in "
                reply += "their hand. Better put some ice on that, should be fine in 2 minutes."

            elif banish_time == 3:
                reply = f"{mention} rolls the dice, slips and shoots themselves in the leg. "
                reply += "The nearest hospital they can afford is in Antarctica, where "
                reply += "they will be spending the next 3 minutes."

            elif banish_time == 4:
                reply = f"{mention} rolls the dice of death, but the gun is jammed. "
                reply += "As they're looking down the barrel something blows up and "
                reply += "hits them in the eye. 4 minutes in Antarctica!"

            else:
                reply = f"{mention} rolls a headshot on the dice of death! 5 minutes in Antarctica!"

            error = await mute_db.carry_out_banish(self.bot, self.mdbname, member, end_date)
            if isinstance(error, Exception):
                if isinstance(error, discord.HTTPException):    http_exception = True
                elif isinstance(error, discord.Forbidden):      forbidden_exception = True
                else:                                           other_exception = True

            if http_exception:
                reply = f"While {mention} did fail and hurt themselves spectacularly in the roulette "
                reply += "there's not much I can do about it due to some stupid HTTP error."
            elif forbidden_exception:
                reply = f"While {mention} did fail and hurt themselves spectacularly in the roulette "
                reply += "there's not much I can do about it because I'm not allowed to banish people."
            elif other_exception:
                reply = f"While {mention} did fail and hurt themselves spectacularly in the roulette "
                reply += "there's not much I can do about it because, uh, reasons. I don't know."

            await ctx.send(reply)

        else:
            # Congratulations bruh!
            response = await ctx.send(f"Sorry chat, seems {mention} will live to see another day.")
            await asyncio.sleep(5)
            await ctx.message.delete()
            await response.delete()

    @discord.ext.commands.command(name="blacklist")
    async def blacklist(self, ctx, *args):
        # TODO add some fancy shenanigans for checking if the user already
        #      is on the blacklist if adding them fails.
        success_list = list()
        failures_list = list()
        for mention in ctx.message.mentions:
            try:
                result = region_db.add_blacklist(
                    self.bot,
                    self.rdbname,
                    self.blacklist_table,
                    mention)
                if result: success_list.append(mention)
                else:      failures_list.append(mention)
            except Exception:
                failures_list.append(mention)


        successes = len(success_list)
        failures = len(failures_list)
        success_mentions = self.bot.mentions_list(success_list)
        failure_mentions = self.bot.mentions_list(failures_list)

        if successes == 0 and failures == 0:
            # No mentions
            await ctx.send(f"{ctx.author.mention} please specify the users you want to blacklist...")

        elif successes > 0 and failures == 0:
            # No failures
            await ctx.send(
                f"{success_mentions} successfully blacklisted! " +
                "They may no longer change their region... unless they change it to Antarctica.")

        elif successes == 0 and failures > 0:
            # No successes
            await ctx.send(
                f"{failure_mentions} could not be blacklisted! Not sure why.")

        else:
            # Mixed result
            await ctx.send(
                f"{success_mentions} successfully blacklisted, but {failure_mentions} could not be blacklisted. " +
                "The ones that could not be blacklisted may already be blacklisted, in which case they can not be blacklisted again.")

    @discord.ext.commands.command(name="unblacklist", aliases=[ "unlist" ])
    async def unblacklist(self, ctx, *args):
        success_list = list()
        failures_list = list()
        for mention in ctx.message.mentions:
            try:
                result = region_db.remove_blacklist(
                    self.bot,
                    self.rdbname,
                    self.blacklist_table,
                    mention)

                if result: success_list.append(mention)
                else:      failures_list.append(mention)
            except Exception as e:
                failures_list.append(mention)

        successes = len(success_list)
        failures = len(failures_list)
        success_mentions = self.bot.mentions_list(success_list)
        failure_mentions = self.bot.mentions_list(failures_list)

        if successes == 0 and failures == 0:
            # No mentions
            await ctx.send(f"{ctx.author.mention} please specify the users you want to unblacklist...")

        elif successes > 0 and failures == 0:
            # No failures
            await ctx.send(
                f"{success_mentions} successfully unblacklisted! " +
                "They may no longer change their region... unless they change it to Antarctica.")

        elif successes == 0 and failures > 0:
            # No successes
            await ctx.send(
                f"{failure_mentions} could not be unblacklisted! " +
                "This may be because they're already banished or something. Who even knows?")

        else:
            # Mixed result
            await ctx.send(
                f"{success_mentions} successfully unblacklisted, but {failure_mentions} could not be blacklisted. " +
                "The unblacklisted ones may not be blacklisted, in which case they can not be unblacklisted again.")

    @discord.ext.commands.command(name="blacklistlist")
    async def blacklistlist(self, ctx, *args):
        result = region_db.fetch_blacklist(
            self.bot,
            self.rdbname,
            self.blacklist_table,
            ctx.guild)

        blacklisted = [ str(ctx.guild.get_member(uid[0])) for uid in result ]
        blacklisted = "\n".join(sorted(blacklisted))
        await ctx.send(f"**{ctx.guild.name}** region blacklist:\n{blacklisted}")

    ###########################################################################
    # Various shenanigans that may need to be implemented into the bot proper #
    # Everything below this line is commented out ATM                         #
    ###########################################################################
    #
    # def check_roles(self, role):
    #     """When roles are created/deleted/updated this function checks that this
    #     doesn't affect which role is antarctica."""
    #     guild = role.guild

    #     old_antarctica = self.antarctica_role[guild.id]
    #     # TODO Delete
    #     # new_antarctica = native.get_antarctica_role(guild)
    #     new_antarctica = self.bot.get_antarctica_role(guild)

    #     if old_antarctica != new_antarctica:
    #         self.antarctica_role[guild.id] = new_antarctica
    #         if new_antarctica is not None:  new_antarctica = f"{var.green}@{new_antarctica}"
    #         else:                       new_antarctica = f"{var.red}undefined"
    #         print(f"{var.cyan}The {var.boldwhite}Antarctica role{var.cyan} in",
    #               f"{var.red}{guild.name}{var.cyan} was updated to: {new_antarctica}{var.reset}")

    # def check_channels(self, channel):
    #     """When channels are created/deleted/updated this function checks that this
    #     doesn't affect which channel is bot-trash, antarctica, etc."""
    #     guild = channel.guild

    #     # Check if antarctica has changed.
    #     old_antarctica  = self.antarctica_channel[guild.id]
    #     # TODO Delete
    #     # new_antarctica  = native.get_antarctica_channel(guild)
    #     new_antarctica  = self.bot.get_antarctica_channel(guild)

    #     if old_antarctica != new_antarctica:
    #         self.antarctica_channel[guild.id] = new_antarctica

    #         if new_antarctica is not None:  new_antarctica = f"{var.green}#{new_antarctica.name}{var.reset}"
    #         else:                       new_antarctica = f"{var.red}undefined"

    #         print(f"{var.cyan}The {var.boldwhite}Antarctica channel{var.cyan} in",
    #               f"{var.red}{guild.name}{var.cyan} was updated to: {new_antarctica}{var.reset}")

    #     # Check if trash has changed.
    #     old_trash       = self.trash_channel[guild.id]
    #     # TODO Delete
    #     # new_trash       = native.get_trash_channel(guild)
    #     new_trash       = self.bot.get_trash_channel(guild)

    #     if old_trash != new_trash:
    #         self.trash_channel[guild.id] = new_trash

    #         if new_trash is not None:   new_trash = f"{var.green}#{new_trash.name}"
    #         else:                   new_trash = f"{var.red}undefined"

    #         print(f"{var.cyan}The {var.boldwhite}trash channel{var.cyan} in",
    #               f"{var.red}{guild.name}{var.cyan} was updated to: {new_trash}{var.reset}")

    # Run check_channels() when a channel is updated somewhere.
    # @commands.Cog.listener()
    # async def on_guild_channel_delete(self, channel):
    #     self.check_channels(channel)

    # @commands.Cog.listener()
    # async def on_guild_channel_create(self, channel):
    #     self.check_channels(channel)

    # @commands.Cog.listener()
    # async def on_guild_channel_update(self, before, after):
    #     self.check_channels(after)

    # # Run check_roles() when a role is updated somewhere.
    # @commands.Cog.listener()
    # async def on_guild_role_create(self, role):
    #     self.check_roles(role)

    # @commands.Cog.listener()
    # async def on_guild_role_delete(self, role):
    #     self.check_roles(role)

    # @commands.Cog.listener()
    # async def on_guild_role_update(self, before, after):
    #     self.check_roles(after)

