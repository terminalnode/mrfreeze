"""
Banish cog.

This cog is for the banish/mute command and the region command.
banish/mute is closely connected to the region command since
they both use the antarctica mechanics.

Therefor they're both in a cog separate from everything else.
"""

import asyncio
import datetime
import logging
import random
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

import discord
from discord import Guild
from discord.ext.commands import CheckFailure
from discord.ext.commands import Context
from discord.ext.commands import command

from mrfreeze.bot import MrFreeze
from mrfreeze.cogs.banish import mute_db
from mrfreeze.cogs.banish.enums import MuteStr
from mrfreeze.cogs.banish.enums import MuteType
from mrfreeze.cogs.banish.templates import templates
from mrfreeze.cogs.cogbase import CogBase
from mrfreeze.lib import checks
from mrfreeze.lib import colors
from mrfreeze.lib.banish import templates as banish_templates

mute_templates: banish_templates.TemplateEngine
mute_command: str
mute_command_aliases: List[str]
template_engine = banish_templates.TemplateEngine()
(mute_command, *mute_command_aliases) = template_engine.get_aliases()

# TODO Delete once template engine is done
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
# TODO Delete above once template engine is done


def setup(bot: MrFreeze) -> None:
    """Load the cog into the bot."""
    bot.add_cog(BanishAndRegion(bot))


class BanishAndRegion(CogBase):
    """Good mod! Read the manual! Or if you're not mod - sod off."""

    def __init__(self, bot: MrFreeze, mdbname: str = "mutes") -> None:
        self.bot = bot
        self.regions: Dict[int, Dict[str, Optional[int]]] = dict()
        self.logger = logging.getLogger(self.__class__.__name__)

        self.antarctica_spellings = (
            "anarctica", "antarctica", "antartica", "anartica",
            "anctartica", "anctarctica", "antacrtica")

        self.regional_aliases = {
            "Asia": [
                "asia", "china", "japan", "thailand", "korea"
            ], "Europe": [
                "europe", "united kingdom", "gb", "great britain", "scandinavia", "germany",
                "sweden", "norway", "spain", "france", "italy", "ireland", "poland", "russia",
                "finland", "estonia", "scotland", "scottland", "portugal"
            ], "North America": [
                "north america", "us", "canada", "mexico", "na", "usa", "united states"
            ], "Africa": [
                "africa", "kongo", "uganda"
            ], "Oceania": [
                "oceania", "australia", "new zealand"
            ], "South America": [
                "south america", "argentina", "chile", "brazil", "peru"
            ], "Middle East": [
                "middleeast", "middle-east", "midleeast", "midle-east", "middleast", "midleast",
                "mesa", "saudi", "saudiarabia", "arabia", "arabian", "middle east", "midle east"
            ]
        }

        # Server setting names
        # Mute interval governs how often to check for unmutes.
        self.mute_interval_name = 'mute_interval'
        self.default_mute_interval = 5
        self.mute_interval_dict: Dict[int, int] = dict()

        # Self mute interval governs how long to banish
        # unauthorized uses of !mute/!banish etc
        self.default_self_mute_time = 20

        # Mutes database creation
        self.mdbname = mdbname
        mdbtable = f"""CREATE TABLE IF NOT EXISTS {self.mdbname}(
            id          integer NOT NULL,
            server      integer NOT NULL,
            voluntary   boolean NOT NULL,
            until       date,
            CONSTRAINT  server_user PRIMARY KEY (id, server));"""
        bot.db_create(self.bot, self.mdbname, mdbtable)

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
    async def on_ready(self) -> None:
        """
        Once ready, do some setup for all servers.

        This is mostly stuff pertaining to banishes and regions, such as setting up the periodic
        unbanish and indexing all the servers' regional roles.
        """
        for server in self.bot.guilds:
            # Set intervals in which to check mutes
            mute_interval = self.bot.read_server_setting(self.bot, server, self.mute_interval_name)
            if mute_interval and mute_interval.isdigit():
                self.mute_interval_dict[server.id] = int(mute_interval)
            else:
                self.mute_interval_dict[server.id] = self.default_mute_interval

            # Add unbanish loop to bot
            self.bot.add_bg_task(self.unbanish_loop(server), f'unbanish@{server.id}')

            # Construct region dict
            self.regions[server.id] = dict()
            for region in self.regional_aliases.keys():
                region_role = discord.utils.get(server.roles, name=region)
                if region_role:
                    self.regions[server.id][region] = region_role.id
                else:
                    self.regions[server.id][region] = None

    async def unbanish_loop(self, server: Guild) -> None:
        """Check for people to unbanish every self.banish_interval seconds."""
        while not self.bot.is_closed():
            await asyncio.sleep(self.mute_interval_dict[server.id])
            self.logger.debug(f"Running unbanish loop for {server.name}.")

            current_time = datetime.datetime.now()
            server_mutes = mute_db.mdb_fetch(self.bot, self.mdbname, server)
            self.logger.debug(f"There are {len(server_mutes)} mutes total in {server.name}.")
            server_mutes = [ i for i in server_mutes if i.until is not None ]
            self.logger.debug(f"There are {len(server_mutes)} timed mutes in {server.name}.")

            mute_role = await self.bot.get_mute_role(server)
            self.logger.debug(f"Mute role in {server.name}: {mute_role}")
            mute_channel = await self.bot.get_mute_channel(server, silent=True)
            self.logger.debug(f"Mute channel in {server.name}: {mute_channel}")
            unmuted = list()

            for mute in server_mutes:
                self.logger.debug(f"Checking if {mute} is due for unbanish.")
                if mute.until < current_time:
                    self.logger.debug(f"{mute} is due for unbanish!")
                    # Need to refresh the member to get their latest roles
                    try:
                        member = await server.fetch_member(mute.member.id)
                    except Exception as e:
                        self.logger.error(f"Failed to refresh muted member: {e}")
                        continue  # Will try again next unbanish loop

                    self.logger.debug(f"Refreshed {member}, they have {len(member.roles)} roles.")

                    # Calculate how late we were in unbanishing
                    diff = self.bot.parse_timedelta(current_time - mute.until)
                    if diff == "":
                        diff = "now"
                    else:
                        diff = f"{diff} ago"

                    # Remove from database
                    mute_db.mdb_del(self.bot, self.mdbname, member, self.logger)

                    if mute_role in member.roles:
                        self.logger.debug(f"{member} has the mute role! Removing it.")
                        try:
                            await member.remove_roles(mute_role)
                            self.logger.debug(f"{member} should no longer have the mute role.")
                            # Members are only considered unmuted if they had the antarctica role
                            unmuted.append(member)

                            log = f"Auto-unmuted {colors.CYAN_B}{member.name}#"
                            log += f"{member.discriminator} @ {server.name}."
                            log += f"{colors.YELLOW} (due {diff}){colors.RESET}"
                            self.logger.info(log)

                        except Exception as e:
                            log = f"Failed to remove mute role of {colors.YELLOW}"
                            log += f"{member.name}#{member.discriminator}"
                            log += f"{colors.CYAN_B} @ {colors.MAGENTA} {server.name}:"
                            log += f"\n{colors.RED}==> {colors.RESET}{e}"
                            self.logger.error(log)
                    else:
                        log = f"User {colors.YELLOW}{member.name}#{member.discriminator}"
                        log += f"{colors.CYAN_B} @ {colors.MAGENTA} {server.name}{colors.CYAN} "
                        log += f"due for unmute but does not have a mute role!{colors.RESET}"
                        self.logger.warning(log)

            # Time for some great regrets
            if len(unmuted) > 0:
                unmuted_str = self.mentions_list(unmuted)
                msg = None

                if len(unmuted_str) == 1:
                    msg = "It's with great regret that I must inform you all that "
                    msg += f"{unmuted_str}'s exile has come to an end."
                else:
                    msg = "It's with great regret that I must inform you all that the exile of "
                    msg += f"{unmuted_str} has come to an end."

                if msg is not None:
                    await mute_channel.send(msg)

    def get_self_mute_time(self, server: Guild) -> int:
        """
        Return the default self-mute time for the server.

        If the server lacks its own self-mute time, the default is returned instead.
        """
        server_smt: Optional[int]
        server_smt = self.bot.get_self_mute_time(server)
        if server_smt:
            return server_smt
        else:
            return self.default_self_mute_time

    @command(
        name="banishinterval",
        aliases=[ "banishint", "baninterval", "banint", "muteinterval", "muteint" ])
    @discord.ext.commands.check(checks.is_owner_or_mod)
    async def _banishinterval(self, ctx: Context, *args: str) -> None:
        author = ctx.author.mention
        server = ctx.guild
        interval = None

        # Look for first number in args and use as interval time.
        for arg in args:
            if arg.isdigit():
                interval = int(arg)
                break

        reply = None
        if interval is None:
            reply = f"{author} You didn't specify a valid interval. Please try again."

        elif interval == self.mute_interval_dict[server.id]:
            reply = f"{author} The interval for this server is already set to {interval}."

        elif interval < 5:
            reply = f"{author} You greedy little smud you, trying to steal my CPU cycles "
            reply += "like that. Minimum interval is 5 seconds."

        else:
            oldinterval = self.mute_interval_dict[server.id]
            self.mute_interval_dict[server.id] = interval
            setting_saved = self.bot.write_server_setting(
                self.bot,
                server,
                self.mute_interval_name, str(interval)
            )

            if setting_saved:
                reply = f"{author} The interval has been changed from {oldinterval} to "
                reply += f"{interval} seconds."
            else:
                reply = f"{author} The interval has been changed from {oldinterval} to "
                reply += f"{interval} seconds, *BUT* for some reason I was unable to save "
                reply += f"this setting, so it will be reset to {oldinterval} once I restart."

        if reply is not None:
            await ctx.send(reply)

    @command(name='selfmutetime', aliases=['smt', 'selfmute', 'mutetime'])
    @discord.ext.commands.check(checks.is_mod)
    async def _selfmutetime(self, ctx: Context, *args: str) -> None:
        author = ctx.author.mention
        server = ctx.guild
        old_time = self.get_self_mute_time(server)
        proposed_time = None

        # Look for first number in args and use as new self mute time.
        for arg in args:
            if arg.isdigit():
                proposed_time = int(arg)
                break

        msg = None
        if proposed_time is None:
            msg = f"{author} Please specify the time in minutes and try again."

        elif proposed_time == old_time:
            msg = f"{author} The self mute time for this server is already set to {proposed_time}."

        elif proposed_time == 0:
            msg = f"{author} Zero is not a valid self mute time, smud."

        elif proposed_time > 3600 * 24 * 7:
            msg = f"{author} I may be evil, but even I think more than a weeks punishment is "
            msg += "a bit harsh..."

        else:
            setting_saved = self.bot.settings.set_self_mute_time(server, proposed_time)

            if setting_saved:
                msg = f"{author} The self mute time has been changed from {old_time} to "
                msg += f"{proposed_time} minutes."
            else:
                msg = f"{author} The self mute time has been changed from {old_time} to "
                msg += f"{proposed_time} minutes, *BUT* for some reason I was unable to "
                msg += f"save this setting, so it will be reset to {old_time} once I restart."

        if msg is not None:
            await ctx.send(msg)

    @command(name=mute_command, aliases=mute_command_aliases)
    @discord.ext.commands.check(checks.is_mod)
    async def _banish(self, ctx: Context, *args: str) -> None:
        """Mute one or more users (can only be invoked by mods)."""
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
        if invocation[:2] == "un":
            unmute = True
        else:
            unmute = False

        is_super = 'super' in invocation
        is_mega = 'mega' in invocation

        if invocation == "banish":
            invocation = MuteType.BANISH
        elif invocation in banish_aliases:
            invocation = MuteType.BANISH
        elif invocation in hogtie_aliases:
            invocation = MuteType.HOGTIE
        elif invocation in mute_aliases:
            invocation = MuteType.MUTE

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
                if is_super:
                    duration += datetime.timedelta(weeks=1)
                elif is_mega:
                    duration += datetime.timedelta(days=365)
                end_date = current_time + duration
            except OverflowError:
                end_date = datetime.datetime.max
                duration = end_date - current_time

        if len(mentions) == 0:
            template = MuteStr.NONE

        elif bot and not unmute:
            # Freeze mutes: FREEZE, FREEZE_SELF, FREEZE_OTHERS
            if len(mentions) == 1:
                template = MuteStr.FREEZE
            elif len(mentions) == 2 and slf:
                template = MuteStr.FREEZE_SELF
            else:
                template = MuteStr.FREEZE_OTHERS
            fails_list = usr + mod

        elif mod and not unmute:
            # Mod mutes: SELF, MOD, MODS
            if len(mentions) == 1 and slf:
                template = MuteStr.SELF
            elif len(mentions) == 1:
                template = MuteStr.MOD
            else:
                template = MuteStr.MODS
            fails_list = mod

        else:
            # Working mutes (at user mutes):
            # SINGLE, MULTI, FAIL, FAILS, SINGLE_FAIL, SINGLE_FAILS, MULTI_FAIL, MULTI_FAILS
            for member in usr:
                if unmute:
                    error = await mute_db.carry_out_unbanish(
                        self.bot,
                        self.mdbname,
                        member,
                        self.logger)
                else:
                    error = await mute_db.carry_out_banish(
                        self.bot,
                        self.mdbname,
                        member,
                        self.logger,
                        end_date)

                if isinstance(error, Exception):
                    fails_list.append(member)
                    if isinstance(error, discord.HTTPException):
                        http_exception = True
                    elif isinstance(error, discord.Forbidden):
                        forbidden_exception = True
                    else:
                        other_exception = True

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

            if single and no_fails and unmute:
                template = MuteStr.UNSINGLE
            elif single and no_fails:
                template = MuteStr.SINGLE
            elif multi and no_fails and unmute:
                template = MuteStr.UNMULTI
            elif multi and no_fails:
                template = MuteStr.MULTI
            elif fail and no_success and unmute:
                template = MuteStr.UNFAIL
            elif fail and no_success:
                template = MuteStr.FAIL
            elif fails and no_success and unmute:
                template = MuteStr.UNFAILS
            elif fails and no_success:
                template = MuteStr.FAILS
            elif single and fail and unmute:
                template = MuteStr.UNSINGLE_FAIL
            elif single and fail:
                template = MuteStr.SINGLE_FAIL
            elif single and fails and unmute:
                template = MuteStr.UNSINGLE_FAILS
            elif single and fails:
                template = MuteStr.SINGLE_FAILS
            elif multi and fail and unmute:
                template = MuteStr.UNMULTI_FAIL
            elif multi and fail:
                template = MuteStr.MULTI_FAIL
            elif multi and fails and unmute:
                template = MuteStr.UNMULTI_FAILS
            elif multi and fails:
                template = MuteStr.MULTI_FAILS

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
        success_str = self.mentions_list(success_list)
        fails_str = self.mentions_list(fails_list)
        errors_string = str()

        if http_exception and forbidden_exception and other_exception:
            errors_string = "**a wild mix of crazy exceptions**"
        elif http_exception and forbidden_exception:
            errors_string = "**a mix of HTTP exception and lack of privilegies**"
        elif http_exception and other_exception:
            errors_string = "**a wild mix of HTTP exception and other stuff**"
        elif forbidden_exception and other_exception:
            errors_string = "**a wild mix of lacking privilegies and some other stuff**"
        elif http_exception:
            errors_string = "**an HTTP exception**"
        elif forbidden_exception:
            errors_string = "**a lack of privilegies**"
        else:
            errors_string = "**an unidentified exception**"

        # Create string
        timestamp = templates[invocation][MuteStr.TIMESTAMP].substitute(
            duration=self.bot.parse_timedelta(duration)
        )

        reply = f"{ctx.author.mention} "
        reply += templates[invocation][template].substitute(
            author=ctx.author.mention,
            victims=success_str,
            fails=fails_str,
            errors=errors_string,
            timestamp=timestamp
        )
        await ctx.send(reply)

    # This decorator makes it discord.py automatically
    # trigger it when _banish throws an error.
    @_banish.error
    async def unauthorized_banish(self, ctx: Context, error: Exception) -> None:
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
        if not isinstance(error, CheckFailure):
            # Only run this on Check Failure.
            return

        mentions = ctx.message.mentions
        author = ctx.author
        server = ctx.guild

        invocation = ctx.invoked_with
        if invocation == "banish":
            invocation = MuteType.BANISH
        elif invocation in banish_aliases:
            invocation = MuteType.BANISH
        elif invocation in hogtie_aliases:
            invocation = MuteType.HOGTIE
        elif invocation in mute_aliases:
            invocation = MuteType.MUTE

        none     = (len(mentions) == 0)
        selfmute = (len(mentions) == 1 and author in mentions)
        mix      = (not selfmute and author in mentions)
        user     = (not selfmute and not mix and len(mentions) > 0)
        fails    = self.mentions_list([ mention for mention in mentions if mention != author ])

        if none:
            template = MuteStr.USER_NONE
        elif selfmute:
            template = MuteStr.USER_SELF
        elif user:
            template = MuteStr.USER_USER
        elif mix:
            template = MuteStr.USER_MIXED

        self_mute_time: Optional[int] = self.get_self_mute_time(server)
        if not (self_mute_time):
            self_mute_time = self.default_self_mute_time

        duration = datetime.timedelta(minutes = float(self_mute_time))
        end_date = datetime.datetime.now() + duration
        duration = self.bot.parse_timedelta(duration)

        # Carry out the banish with resulting end date
        banish_error = await mute_db.carry_out_banish(
            self.bot,
            self.mdbname,
            author,
            self.logger,
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
            template = MuteStr.USER_FAIL

        reply = templates[invocation][template].substitute(
            author=author.mention, fails=fails, errors=error_msg, timestamp=duration
        )

        await ctx.send(reply)

    @command(name="banishtime", aliases=["amibanished", "howmuchlonger"])
    async def banishtime(self, ctx: Context) -> None:
        """Check how long until you're unbanished."""
        banish_list: List[mute_db.BanishTuple]
        banish_list = mute_db.mdb_fetch(self.bot, self.mdbname, ctx.author)
        mention = ctx.author.mention

        msg: Optional[str] = None
        if not banish_list:
            msg = f"{mention} You're not banished right now."

        else:
            until = banish_list[0].until
            left: str
            now = datetime.datetime.now()

            if until and until < now:
                msg = f"{mention} You're due for unbanishment. Hold on a sec."

            else:
                if until:
                    left = self.bot.parse_timedelta(until - now)
                else:
                    left = "an eternity"
                msg = f"{mention} You have about **{left}** left to go."

        if msg:
            await ctx.send(msg)

    @command(name="roulette")
    async def roulette(self, ctx: Context, *args: str) -> None:
        """Roll the dice and test your luck, banish or nothing."""
        member = ctx.author
        mention = member.mention
        http_exception = False
        forbidden_exception = False
        other_exception = False

        penposium = 444289793141112864
        bot_trash = 471909336377982976
        bots = 445708393789915146

        # Skip if server is Penposium and channel isn't #bot-trash or #bots
        if ctx.guild.id == penposium and ctx.channel.id not in (bot_trash, bots):
            await ctx.send("Please only use that command in the bot-trash channel... smud.")
            return

        if random.randint(1, 6) == 1:
            # Tough luck, yer goin' down

            banish_time = random.randint(1, 5)
            duration = datetime.timedelta(minutes = banish_time)
            end_date = datetime.datetime.now() + duration
            msg = "I should probably say something now... but I don't know what."

            if banish_time == 1:
                msg = f"{mention} rolls the dice, the gun doesn't fire but somehow "
                msg += "they manage to hurt themselves with it anyway. A minute in "
                msg += "Antarctica and they'll be good as new!"

            elif banish_time == 2:
                msg = f"{mention} rolls the dice, but the gun misfires and explodes in "
                msg += "their hand. Better put some ice on that, should be fine in 2 minutes."

            elif banish_time == 3:
                msg = f"{mention} rolls the dice, slips and shoots themselves in the leg. "
                msg += "The nearest hospital they can afford is in Antarctica, where "
                msg += "they will be spending the next 3 minutes."

            elif banish_time == 4:
                msg = f"{mention} rolls the dice of death, but the gun is jammed. "
                msg += "As they're looking down the barrel something blows up and "
                msg += "hits them in the eye. 4 minutes in Antarctica!"

            else:
                msg = f"{mention} rolls a headshot on the dice of death! 5 minutes in Antarctica!"

            error = await mute_db.carry_out_banish(
                self.bot,
                self.mdbname,
                member,
                self.logger,
                end_date
            )

            if isinstance(error, Exception):
                if isinstance(error, discord.HTTPException):
                    http_exception = True
                elif isinstance(error, discord.Forbidden):
                    forbidden_exception = True
                else:
                    other_exception = True

            if http_exception:
                msg = f"While {mention} did fail and hurt themselves spectacularly in the "
                msg += "roulette there's not much I can do about it due to some stupid HTTP error."
            elif forbidden_exception:
                msg = f"While {mention} did fail and hurt themselves spectacularly in the "
                msg += "roulette there's not much I can do about it because I'm not allowed "
                msg += "to banish people."
            elif other_exception:
                msg = f"While {mention} did fail and hurt themselves spectacularly in the "
                msg += "roulette there's not much I can do about it because, uh, reasons. "
                msg += "I don't know."

            await ctx.send(msg)

        else:
            # Congratulations bruh!
            response = await ctx.send(f"Sorry chat, seems {mention} will live to see another day.")
            await asyncio.sleep(5)
            await ctx.message.delete()
            await response.delete()

    @command(name="region", aliases=["regions"])
    async def _region(self, ctx: Context, *args: str) -> None:
        """Assign yourself a colourful regional role."""
        args = tuple([ a.lower() for a in args ])

        if len(args) == 0 or "help" in args:
            msg = "Type !region followed by your region, this will assign you a regional role "
            msg += "with an associated snazzy colour for your nick. These roles are not "
            msg += "highlightable and only serve to show people where you're from. \n\n"
            msg += "The available regions are:\n"
            msg += " - Asia\n - Europe\n - North America\n - South America\n"
            msg += " - Africa\n - Oceania\n - Middle East"
            await ctx.send(msg)
            return

        if "list" in args:
            msg = "Available regions:\n"
            msg += " - Asia\n - Europe\n - North America\n - South America\n"
            msg += " - Africa\n - Oceania\n - Middle East"
            await ctx.send(msg)
            return

        if await self.region_antarctica(ctx, args):
            return

        await self.set_region(ctx, args)

    async def region_antarctica(self, ctx: Context, args: Tuple[str, ...]) -> bool:
        """
        Analyze arguments to see if user tried to set region to Antarctica.

        If they did, the method will return True, banish them and send some snarky repyl.
        Otherwise it returns False.
        """
        # Check if the user tried to set region to Antarctica
        said_antarctica = False
        for variant in self.antarctica_spellings:
            if variant in args:
                said_antarctica = True
                spelling = variant
                break

        if not said_antarctica:
            return False

        # User confirmed to have tried to set region to Antarctica
        # Initiating punishment
        reply = f"{ctx.author.mention} is a filthy *LIAR* claiming to live in Antarctica. "

        if spelling == "antarctica":
            duration = datetime.timedelta(minutes = 10)
            end_date = datetime.datetime.now() + duration
            duration = self.bot.parse_timedelta(duration)
            reply += "I'll give them what they want and banish them to that "
            reply += "frozen hell for ten minutes!"

        else:
            duration = datetime.timedelta(minutes = 20)
            end_date = datetime.datetime.now() + duration
            duration = self.bot.parse_timedelta(duration)
            reply += f"What's more, they spelled it *{spelling.capitalize()}* "
            reply += "instead of *Antarctica*... 20 minutes in Penguin school "
            reply += "ought to teach them some manners!"

        # Carry out the banish with resulting end date
        error = await mute_db.carry_out_banish(
            self.bot,
            self.mdbname,
            ctx.author,
            self.logger,
            end_date
        )
        if isinstance(error, Exception):
            reply = f"{ctx.author.mention} is a filthy *LIAR* claiming to live in Antarctica. "
            reply += "Unfortunately there doesn't seem to be much I can do about that. Not sure "
            reply += "why. Some kind of system malfunction or whatever."

        await ctx.send(reply)
        return True

    async def set_region(self, ctx: Context, args: Tuple[str, ...]) -> None:
        """
        Set the region of a user based on what they said.

        Determine which region the user tried to set using the !region command,
        then set that region (if found) and send an appropriate response. If
        the region isn't found don't set a role, just send an appropriate response.
        """
        regions = self.regions[ctx.guild.id]
        author_roles = [ i.id for i in ctx.author.roles if i.name not in regions.keys() ]
        all_args = " ".join(args)

        found_region = False
        valid_region = True
        for region in self.regional_aliases:
            if found_region:
                break

            for alias in self.regional_aliases[region]:
                if alias in all_args:
                    author_roles.append(regions[region])
                    valid_region = regions[region] is not None
                    new_role_name = region
                    found_region = True

        if found_region and valid_region:
            new_roles = [ discord.Object(id=i) for i in author_roles ]
            await ctx.author.edit(roles=new_roles)

            msg = f"{ctx.author.mention} You've been assigned a new role, "
            msg += f"welcome to {new_role_name}!"
        else:
            msg = f"{ctx.author.mention} I couldn't find a match for {' '.join(args)}.\n"
            msg += "Please check your spelling or type **!region list** for a list of "
            msg += "available regions."
        await ctx.send(msg)
