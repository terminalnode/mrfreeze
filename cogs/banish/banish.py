import discord                      # Basic discord functionality
import asyncio                      # Required for the unbanish loop
import datetime                     # Required for outputing the time until / duration of banishes to the log
from internals import checks        # Required to check who's allowed to issue these commands

# Importing the banish submodules
from .enums import *
from .templates import *
from .mute_aliases import *
from .mute_db import *

# This cog is for the banish/mute command and the region command.
# banish/mute is closely connected to the region command since they both use the antarctica mechanics.
# Therefor they're both in a cog separate from everything else.

def setup(bot):
    bot.add_cog(BanishRegionCog(bot))

class BanishRegionCog(discord.ext.commands.Cog, name='BanishRegionCog'):
    """Good mod! Read the manual! Or if you're not mod - sod off!"""
    def __init__(self, bot, mdbname="mutes", rdbname="regions"):
        self.bot = bot

        # Server setting names
        # Mute interval governs how often to check for unmutes.
        self.mute_interval_name = 'mute_interval'
        self.default_mute_interval = 5
        self.mute_interval_dict = dict()

        # Self mute interval governs how long to banish unauthorized uses of !mute/!banish etc
        self.self_mute_time_name = 'self_mute_time'
        self.default_self_mute_time = 20
        self.self_mute_time_dict = dict()

        # Mutes database creation
        self.mdbname = mdbname
        # Complete list of tables and their rows in this database.
        # Primary key(s) is marked with an asterisk (*).
        # Mandatory but not primary keys are marked with a pling (!).
        # TABLE         ROWS        TYPE        FUNCTION
        # self.mdbname  id*         integer     User ID
        #               server*     integer     Server ID
        #               voluntary!  boolean     If this mute was self-inflicted or not.
        #               until       date        The date when the user should be unbanned.
        #                                       Leave empty if indefinite.
        mdbtable = f"""CREATE TABLE IF NOT EXISTS {self.mdbname}(
            id          integer NOT NULL,
            server      integer NOT NULL,
            voluntary   boolean NOT NULL,
            until       date,
            CONSTRAINT  server_user PRIMARY KEY (id, server));"""
        bot.db_create(self.bot, self.mdbname, mdbtable)

        # Region database creation
        self.rdbname = rdbname
        # Complete list of tables and their rows in this database.
        # Primary key(s) is marked with an asterisk (*).
        # Mandatory but not primary keys are marked with a pling (!).
        # TABLE             ROWS        TYPE        FUNCTION
        # self.rdbname      role*       integer     Role ID
        #                   server*     integer     Server ID
        #                   triggers!   string      String of keywords for the region
        # self.rdbname_bl   uid*        integer     User ID
        #                   sid*        integer     Server ID
        rdbtable = f"""CREATE TABLE IF NOT EXISTS {self.rdbname}(
            role        integer NOT NULL,
            server      integer NOT NULL,
            triggers    str NOT NULL,
            CONSTRAINT  server_user PRIMARY KEY (role, server));"""

        rdbtable_bl = f"""CREATE TABLE IF NOT EXISTS {self.rdbname}_bl(
            uid         integer NOT NULL,
            sid         integer NOT NULL,
            CONSTRAINT  sid_uid PRIMARY KEY (uid, sid));"""

        bot.db_create(self.bot, self.rdbname, rdbtable, comment="region table")
        bot.db_create(self.bot, self.rdbname, rdbtable_bl, comment="blacklist table")

    @discord.ext.commands.Cog.listener()
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

    async def unbanish_loop(self, server):
        """This loop checks for people to unbanish every self.banish_interval seconds.""" 
        while not self.bot.is_closed():
            await asyncio.sleep(self.mute_interval_dict[server.id])

            current_time = datetime.datetime.now()
            server_mutes = mdb_fetch(self.bot, self.mdbname, server)
            mute_role = self.bot.servertuples[server.id].mute_role
            mute_channel = self.bot.servertuples[server.id].mute_channel
            unmuted = list()

            for mute in server_mutes:
                if mute.until == None:
                    continue
                
                member = mute.member
                until = mute.until

                if until < current_time:
                    diff = self.bot.parse_timedelta(current_time - until)
                    if diff == "":  diff = "now"
                    else:           diff = f"{diff} ago"

                    mdb_del(self.bot, self.mdbname, member) # Remove from database
                    if mute_role in member.roles:
                        try:
                            await member.remove_roles(mute_role)
                            # Members are only considered unmuted if they had the antarctica role
                            unmuted.append(member)
                        except Exception as e:
                            print(f"{self.bot.current_time()} {self.bot.RED_B}Mutes DB:{self.bot.CYAN} failed to remove " +
                                f"mute role of{self.bot.CYAN_B} {member.name}#{member.discriminator} @ {server.name}.\n" +
                                f"{self.bot.RED}==> {e}")

                    print(f"{self.bot.current_time()} {self.bot.GREEN_B}Mutes DB:{self.bot.CYAN} auto-unmuted " +
                        f"{self.bot.CYAN_B}{member.name}#{member.discriminator} @ {server.name}." +
                        f"{self.bot.YELLOW} (due {diff}){self.bot.RESET}")

            # Time for some great regrets
            if len(unmuted) > 0:
                unmuted = self.bot.mentions_list(unmuted)
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
        
        if interval == None:
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

        if proposed_time == None:
            await ctx.send(f"{author} Please specify the time in minutes and try again.")

        elif proposed_time == self.self_mute_time_dict[server.id]:
            await ctx.send(f"{author} The self mute time for this server is already set to {proposed_time}.")

        elif proposed_time == 0:
            await ctx.send(f"{author} Zero is not a valid self mute time, smud.")

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

        invocation = ctx.invoked_with
        if invocation[:2] == "un":  unmute = True
        else:                       unmute = False

        if invocation == "banish":          invocation = MuteType.BANISH
        elif invocation in banish_aliases:  invocation = MuteType.BANISH
        elif invocation in hogtie_aliases:  invocation = MuteType.HOGTIE
        elif invocation in mute_aliases:    invocation = MuteType.MUTE

        duration, end_date = self.bot.extract_time(args)

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
                if unmute:  error = await self.carry_out_unbanish(self.bot, self.mdbname, member)
                else:       error = await self.carry_out_banish(self.bot, self.mdbname, member, end_date)

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
        success_list = self.bot.mentions_list(success_list)
        fails_list = self.bot.mentions_list(fails_list)
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

    @_banish.error
    async def _banish_error(self, ctx, error):
        """Try (and fail) to mute one or more users (can only be invoked by non-mods)"""

        if not isinstance(error, discord.ext.commands.CheckFailure):
            # Only run this on Check Failure.
            return

        # Only three cases to check for in this function:
        # USER_NONE     # User invoked mute with no arguments
        # USER_SELF     # User tried muting themselves
        # USER_USER     # User tried muting other user(s)
        # USER_MIXED    # User tried musing themselves and other user(s)
        
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
        fails    = self.bot.mentions_list([ mention for mention in mentions if mention != author ])

        if none:        template = MuteStr.USER_NONE
        elif selfmute:  template = MuteStr.USER_SELF
        elif user:      template = MuteStr.USER_USER
        elif mix:       template = MuteStr.USER_MIXED

        duration = datetime.timedelta(minutes = self.self_mute_time_dict[server.id])
        end_date = datetime.datetime.now() + duration
        duration = self.bot.parse_timedelta(duration)
        error = await self.carry_out_banish(self.bot, self.mdbname, author, end_date)

        if isinstance(error, Exception):
            if isinstance(error, discord.Forbidden):        error = "**a lack of privilegies**"
            elif isinstance(error, discord.HTTPException):  error = "**an HTTP exception**"
            else:                                           error = "**an unknown error**"
            template = MuteStr.USER_FAIL

        reply=templates[invocation][template].substitute(
            author=author.mention, fails=fails, errors=error, timestamp=duration
        )

        await ctx.send(reply)


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
    #         if new_antarctica != None:  new_antarctica = f"{var.green}@{new_antarctica}"
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

    #         if new_antarctica != None:  new_antarctica = f"{var.green}#{new_antarctica.name}{var.reset}"
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

    #         if new_trash != None:   new_trash = f"{var.green}#{new_trash.name}"
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

