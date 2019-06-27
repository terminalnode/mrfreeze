import discord                      # Basic discord functionality
import asyncio                      # Required for the unbanish loop
import datetime                     # Required for outputing the time until / duration of banishes to the log
from string import Template         # Required to generate a wide variety of responses
from collections import namedtuple  # Required for producing the output of the mdb_fetch()/db_parse()
from internals import checks        # Required to check who's allowed to issue these commands
from enum import Enum, auto         # Used for the templates dictionary

# This cog is for the banish/mute command and the region command.
# banish/mute is closely connected to the region command since they both use the antarctica mechanics.
# Therefor they're both in a cog separate from everything else.

def setup(bot):
    bot.add_cog(BanishRegionCog(bot))

# Beloved child has many names.
banish_aliases =  [          'unbanish', 'microbanish', 'superbanish', 'SUPERBANISH', 'megabanish', 'MEGABANISH']
hogtie_aliases =  ['hogtie', 'unhogtie', 'microhogtie', 'superhogtie', 'SUPERHOGTIE', 'megahogtie', 'MEGAHOGTIE']
hogtie_aliases += ['tie',    'untie',    'microtie',    'supertie',    'SUPERTIE',    'megatie',    'MEGATIE']
mute_aliases =    ['mute',   'unmute',   'micromute',   'supermute',   'SUPERMUTE',   'megamute',   'MEGAMUTE']
all_aliases = banish_aliases + hogtie_aliases + mute_aliases

# Templates for the various responses. There are lots of them.
class MuteType(Enum):
    MUTE      = "muted"
    BANISH    = "banished"
    HOGTIE    = "hogtied"

class MuteStr(Enum):
    """Various categories of !mute attempts."""
    # MrFreeze
    FREEZE              = auto()    # Tried muting: MrFreeze
    FREEZE_SELF         = auto()    # Tried muting: MrFreeze + only self
    FREEZE_OTHERS       = auto()    # Tried muting: MrFreeze + others (possibly including self)
    # Mod mutes (any added users will just be ignored for simplicity)
    SELF                = auto()    # Tried muting: self
    MOD                 = auto()    # Tried muting: a single mod
    MODS                = auto()    # Tried muting: several mods (possibly including self)
    # At user mutes (mods muting users)
    NONE                = auto()    # No mentions in list
    SINGLE              = auto()    # Successfully muted one
    MULTI               = auto()    # Successfully muted more than one
    FAIL                = auto()    # Failed to mute one
    FAILS               = auto()    # Failed to mute more than one
    SINGLE_FAIL         = auto()    # Successfully muted one, failed to mute one
    SINGLE_FAILS        = auto()    # Successfully muted one, failed to mute more than one
    MULTI_FAIL          = auto()    # Successfully muted more than one, failed to mute one
    MULTI_FAILS         = auto()    # Successfully muted more than one, failed to mute more than one
    # By user mutes (users trying to mute)
    USER_SELF           = auto()    # User tried muting themselves
    USER_USER           = auto()    # User tried muting other user(s)
    USER_MIXED          = auto()    # User tried musing themselves and other user(s)
    # Timestamp
    TIMESTAMP           = auto()    # The time stamp appended to the end of the message

templates = dict()
# Initial mention of author will be added before all of these.

templates[MuteType.MUTE] = {
    # MrFreeze
    MuteStr.FREEZE          : Template("No *you* shut up!"),
    MuteStr.FREEZE_SELF     : Template("If you shut up, I shut up. Deal?"),
    MuteStr.FREEZE_OTHERS   : Template("If you could silence me you would've done so long ago, now $fails on the other hand... just give me the word."),
    # Mod mutes (any added users will just be ignored for simplicity)
    MuteStr.SELF            : Template("Believe me, if I could've I would've muted you the day I walked in here."),
    MuteStr.MOD             : Template("Look, nobody likes $fails but they're a mod so we're stuck with them."),
    MuteStr.MODS            : Template("Look, nobody likes $fails, but they're mods so we're stuck with them."),
    # At user mutes (mods muting users)
    MuteStr.NONE            : Template("You want me to mute... no one? Well, that makes my job easy."),
    MuteStr.SINGLE          : Template("About time! $victims has been muted. $timestamp"),
    MuteStr.MULTI           : Template("About time! $victims have been muted. $timestamp"),
    MuteStr.FAIL            : Template("Due to $errors it seems I was unable to mute $fails. Damn shame."),
    MuteStr.FAILS           : Template("Due to $errors it seems I was unable to mute $fails. Damn shame."),
    MuteStr.SINGLE_FAIL     : Template("About time! $victims has been muted. $timestamp However due to $errors I was unable to mute $fails."),
    MuteStr.SINGLE_FAILS    : Template("About time! $victims has been muted. $timestamp However due to $errors I was unable to mute $fails."),
    MuteStr.MULTI_FAIL      : Template("About time! $victims have been muted. $timestamp However due to $errors I was unable to mute $fails."),
    MuteStr.MULTI_FAILS     : Template("About time! $victims have been muted. $timestamp However due to $errors I was unable to mute $fails."),
    # By users mutes (users trying to mute)
    MuteStr.USER_SELF       : Template("Muting yourself, that's a new one. Have you tried just not talking so damn much?"),
    MuteStr.USER_USER       : Template("I hate $victims too, but I hate you more so... nope."),
    MuteStr.USER_MIXED      : Template("Those are some prime victims you've got there, too bad I don't listen to you."),
    # Timestamp (appeneded to the original message)
    MuteStr.TIMESTAMP       : Template("This will last for about $duration."),
}

templates[MuteType.BANISH] = {
    # MrFreeze
    MuteStr.FREEZE          : Template("OK, I'll just march right on home then."),
    MuteStr.FREEZE_SELF     : Template("Oh heeeeell no! This is my realm and you're not invited."),
    MuteStr.FREEZE_OTHERS   : Template("If you think I'm spending a second more than necessary with $fails you're gravely mistaken."),
    # Mod mutes
    MuteStr.SELF            : Template("Oh heeeeell no! This is my realm and you're not invited."),
    MuteStr.MOD             : Template("Sorry, I have a strict no mods-policy at home."),
    MuteStr.MODS            : Template("Oh yay, mod party at my house! Me, $fails can have long enthralling talks on server policy all night! On second thought... PASS."),
    # At user mutes (mods muting users)
    MuteStr.NONE            : Template("Oki-doki, zero banishes coming up! That's OK, I like solitude. $timestamp"),
    MuteStr.SINGLE          : Template("Good work! The filthy smud $victims has been banished! $timestamp"),
    MuteStr.MULTI           : Template("Good work! The filthy smuds $victims have been banished! $timestamp"),
    MuteStr.FAIL            : Template("Seems $fails is banned from going to Antarctica after having caused $errors there a few years back."),
    MuteStr.FAILS           : Template("Seems $fails is banned from going to Antarctica after having caused $errors there a few years back."),
    MuteStr.SINGLE_FAIL     : Template("Good work! The filthy smud $victims has been banished! $timestamp However it seems $fails is banned from going to Antarctica after having caused $errors there a few years back."),
    MuteStr.SINGLE_FAILS    : Template("Good work! The filthy smud $victims has been banished! $timestamp However it seems $fails are banned from going to Antarctica after having caused $errors there a few years back."),
    MuteStr.MULTI_FAIL      : Template("Good work! The filthy smuds $victims have been banished! $timestamp However it seems $fails is banned from going to Antarctica after having caused $errors there a few years back."),
    MuteStr.MULTI_FAILS     : Template("Good work! The filthy smuds $victims have been banished! $timestamp However it seems $fails are banned from going to Antarctica after having caused $errors there a few years back."),
    # By users mutes (users trying to mute)
    MuteStr.USER_SELF       : Template("You're not allowed to banish anyone, including yourself."),
    MuteStr.USER_USER       : Template("I hate $victims too, but I hate you more so... nah."),
    MuteStr.USER_MIXED      : Template("I'm not letting *anyone* in here unless the mods force me to."),
    # Timestamp (appeneded to the original message)
    MuteStr.TIMESTAMP       : Template("They will be stuck in the frozen hells of Antarctica for a good $duration."),
}

templates[MuteType.HOGTIE] = {
    # MrFreeze
    MuteStr.FREEZE          : Template("Hogtie myself? Why don't you come over here and make me?!"),
    MuteStr.FREEZE_SELF     : Template("As lovely as it would be to be tied together with your smuddy ass, I think I'm gonna have to pass."),
    MuteStr.FREEZE_OTHERS   : Template("I can think of at least a thousand things I'd rather do than tie myself to those smuds."),
    # Mod mutes
    MuteStr.SELF            : Template("You're into some kinky shit, I'll give you that."),
    MuteStr.MOD             : Template("Oh get a room you two..."),
    MuteStr.MODS            : Template("As much as I'd love to participate in your kink fest, it seems I'm all out of rope."),
    # At user mutes (mods muting users)
    MuteStr.NONE            : Template("Right, zero hogties coming up. That's saving me a lot of rope."),
    MuteStr.SINGLE          : Template("$victims is all tied up and ready, just the way you like it... $timestamp"),
    MuteStr.MULTI           : Template("$victims are all tied up nice and tight. Don't know why and don't want to know. $timestamp"),
    MuteStr.FAIL            : Template("The ropes snapped and I wasn't able to tie $fails. The ropes most likely suffered from $errors."),
    MuteStr.FAILS           : Template("The ropes snapped and I wasn't able to tie $fails. The ropes most likely suffered from $errors."),
    MuteStr.SINGLE_FAIL     : Template("I was able to tie $victims up nice and tight, but my ropes snapped due to $errors before I was able to do the same to $fails. $timestamp"),
    MuteStr.SINGLE_FAILS    : Template("I was able to tie $victims up nice and tight, but my ropes snapped due to $errors before I was able to do the same to $fails. $timestamp"),
    MuteStr.MULTI_FAIL      : Template("I was able to tie $victims up nice and tight, but my ropes snapped due to $errors before I was able to do the same to $fails. $timestamp"),
    MuteStr.MULTI_FAILS     : Template("I was able to tie $victims up nice and tight, but my ropes snapped due to $errors before I was able to do the same to $fails. $timestamp"),
    # By users mutes (users trying to mute)
    MuteStr.USER_SELF       : Template("Trying to hogtie yourself... good luck with that?"),
    MuteStr.USER_USER       : Template("I hate $victims too, but I hate you more so... nah."),
    MuteStr.USER_MIXED      : Template("..."),
    # Timestamp (appeneded to the original message)
    MuteStr.TIMESTAMP       : Template("The knots will last for about $duration."),
}

class BanishRegionCog(discord.ext.commands.Cog, name='BanishRegionCog'):
    """Good mod! Read the manual! Or if you're not mod - sod off!"""
    def __init__(self, bot, mdbname="mutes", rdbname="regions"):
        self.bot = bot
        self.default_interval = 5
        self.mute_intervals = dict()
        self.BanishTuple = namedtuple('BanishTuple', ['member', 'voluntary', 'until'])

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
        bot.db_create(self.mdbname, mdbtable)

        # Region database creation
        self.rdbname = rdbname
        # Complete list of tables and their rows in this database.
        # Primary key(s) is marked with an asterisk (*).
        # Mandatory but not primary keys are marked with a pling (!).
        # TABLE         ROWS        TYPE        FUNCTION
        # self.rdbname  role*       integer     Role ID
        #               server*     integer     Server ID
        #               triggers!   string      String of keywords for the region
        rdbtable = f"""CREATE TABLE IF NOT EXISTS {self.rdbname}(
            role        integer NOT NULL,
            server      integer NOT NULL,
            triggers    str NOT NULL,
            CONSTRAINT  server_user PRIMARY KEY (role, server));"""
        bot.db_create(self.rdbname, rdbtable)

        # Server setting names
        self.interval = 'mute_interval'

    @discord.ext.commands.Cog.listener()
    async def on_ready(self):
        for server in self.bot.guilds:
            server_interval = self.bot.read_server_setting(server, self.interval)
            if server_interval:
                try:
                    self.mute_intervals[server.id] = int(server_interval)
                except:
                    pass

            self.bot.add_bg_task(self.unbanish_loop(server), f'unbanish@{server.id}')

    async def unbanish_loop(self, server):
        """This loop checks for people to unbanish every self.banish_interval seconds.""" 
        if not server.id in self.mute_intervals:
            self.mute_intervals[server.id] = self.default_interval

        while not self.bot.is_closed():
            await asyncio.sleep(self.mute_intervals[server.id])

            current_time = datetime.datetime.now()
            server_mutes = self.mdb_fetch(server)
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
                    if diff != "":  diff = f"{diff} ago"
                    else:           diff = "now"

                    self.mdb_del(member) # Remove from database
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
        
        if interval == None:
            await ctx.send(f"{author} You didn't specify a valid interval. Please try again.")

        elif interval == self.mute_intervals[server.id]:
            await ctx.send(f"{author} The interval for this server is already set to {interval}.")

        elif interval < 5:
            await ctx.send(f"{author} You greedy little smud you, trying to steal my CPU cycles like that. Minimum interval is 5 seconds.")

        else:
            oldinterval = self.mute_intervals[server.id]
            self.mute_intervals[server.id] = interval
            setting_saved = self.bot.write_server_setting(server, self.interval, str(interval))
            if setting_saved:
                await ctx.send(f"{author} The interval has been changed from {oldinterval} to {interval} seconds.")
            else:
                await ctx.send(f"{author} The interval has been changed from {oldinterval} to {interval} seconds, *BUT* " +
                    f"for some reason I was unable to save this setting, so it will be reset to {oldinterval} once I restart.")

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

        elif unmute:
            # Unmuting muted users
            pass

        else:
            # Working mutes (at user mutes):
            # SINGLE, MULTI, FAIL, FAILS, SINGLE_FAIL, SINGLE_FAILS, MULTI_FAIL, MULTI_FAILS
            for member in usr:
                error = await self.carry_out_banish(member, end_date)

                if isinstance(error, Exception):
                    fails_list.append(member)
                    if isinstance(error, discord.HTTPException):    http_exception = True
                    elif isinstance(error, discord.Forbidden):      forbidden_exception = True
                    else:                                           other_exception = True

                else:
                    success_list.append(member)

            successes   = len(success_list)
            no_success  = (successes == 0)
            single      = (successes == 1)
            multi       = (successes > 1)
            failures    = len(fails_list)
            no_fails    = (failures == 0)
            fail        = (failures == 1)
            fails       = (failures > 1)

            if single and no_fails:     template = MuteStr.SINGLE
            elif multi and no_fails:    template = MuteStr.MULTI
            elif fail and no_success:   template = MuteStr.FAIL
            elif fails and no_success:  template = MuteStr.FAILS
            elif single and fail:       template = MuteStr.SINGLE_FAIL
            elif single and fails:      template = MuteStr.SINGLE_FAILS
            elif multi and fail:        template = MuteStr.MULTI_FAIL
            elif multi and fails:       template = MuteStr.MULTI_FAILS

        # TESTING THINGIE - leave commented unless testing
        # fails_list = success_list
        # template = MuteStr.FAIL
        # template = MuteStr.FAILS
        # template = MuteStr.SINGLE_FAIL
        # template = MuteStr.SINGLE_FAILS
        # template = MuteStr.MULTI_FAIL
        # template = MuteStr.MULTI_FAILS
        # template = MuteStr.MULTI_FAIL
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
        else:                                                           error = "**some unidentified error**"

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

        await ctx.send("special banish error")

    async def carry_out_banish(self, member, end_date):
        """Add the antarctica role to a user, then add them to the db.
        Return None if successfull, Exception otherwise."""
        server = member.guild
        roles = member.roles
        mute_role = self.bot.servertuples[server.id].mute_role
        result = True

        if mute_role not in roles:
            try:                    await member.add_roles(mute_role)
            except Exception as e:  result = e

        if not isinstance(result, Exception):
            self.mdb_add(member, end_date=end_date)

        return result

    ###################################################
    # Below are all commands relating to the database #
    # (they are numerous and need a separete section) #
    ###################################################

    @discord.ext.commands.command(name='dbadd')
    @discord.ext.commands.check(checks.is_owner)
    async def _dbadd(self, ctx, *args):
        """Tests adding users to the database."""
        for mention in ctx.message.mentions:
            self.mdb_add(mention)

    @discord.ext.commands.command(name='dbtime')
    @discord.ext.commands.check(checks.is_owner)
    async def _dbtime(self, ctx, *args):
        """Tests adding users to the database for 30 seconds."""
        until = datetime.datetime.now() + datetime.timedelta(seconds=30)
        for mention in ctx.message.mentions:
            self.mdb_add(mention, end_date=until, prolong=True)

    @discord.ext.commands.command(name='dbcheck')
    @discord.ext.commands.check(checks.is_owner)
    async def _dbcheck(self, ctx, *args):
        """Tests mdb_fetch to see that it outputs with useful parsing."""
        # Server fetch
        server = ctx.guild
        serveroutput = str()
        serverfetch = self.mdb_fetch(server)
        for entry in serverfetch:
            member = entry.member
            voluntary = entry.voluntary
            serveroutput += "\n---------------\n"
            serveroutput += f"Member:    {entry.member}\n"
            serveroutput += f"Voluntary: {entry.voluntary}\n"
            serveroutput += f"Until:     {entry.until}"
        print(f"Server output ({len(serverfetch)} entries):{serveroutput}")

        # User fetch
        for mention in ctx.message.mentions:
            userfetch = self.mdb_fetch(mention)
            if len(userfetch) == 0:
                print(f"No entry for {mention.name}#{mention.discriminator}")
            else:
                print(userfetch)

    @discord.ext.commands.command(name='dbdel')
    @discord.ext.commands.check(checks.is_owner)
    async def _dbdel(self, ctx, *args):
        """Test removing users from the database."""
        for mention in ctx.message.mentions:
            self.mdb_del(mention)

    @discord.ext.commands.command(name='dbfetch')
    @discord.ext.commands.check(checks.is_owner)
    async def _dbfetch(self, ctx, *args):
        """Test listing all mutes on a server."""
        pass

    def mdb_del(self, user):
        """Removes a user from the mutes database."""
        is_member = isinstance(user, discord.Member)
        if not is_member:
            # This should never happen, no point in even logging it.
            raise TypeError(f"Expected discord.Member, got {type(user)}")

        uid = user.id
        server = user.guild.id
        servername = user.guild.name
        name = f"{user.name}#{user.discriminator}"

        is_muted = len(self.mdb_fetch(user)) != 0
        if not is_muted:
            print(f"{self.bot.current_time()} {self.bot.GREEN_B}Mutes DB:{self.bot.CYAN} user already not in DB: " +
                f"{self.bot.CYAN_B}{name} @ {servername}{self.bot.CYAN}.{self.bot.RESET}")
            return True
    
        with self.bot.db_connect(self.mdbname) as conn:
            c = conn.cursor()
            sql = f"DELETE FROM {self.mdbname} WHERE id = ? AND server = ?"
    
            try:
                c.execute(sql, (uid, server))
                print(f"{self.bot.current_time()} {self.bot.GREEN_B}Mutes DB:{self.bot.CYAN} removed user from DB: " +
                    f"{self.bot.CYAN_B}{name} @ {servername}{self.bot.CYAN}.{self.bot.RESET}")
                return True
    
            except Exception as error:
                print(f"{self.bot.current_time()} {self.bot.RED_B}Mutes DB:{self.bot.CYAN} failed to remove from DB: " +
                    f"{self.bot.CYAN_B}{name} @ {servername}{self.bot.CYAN}:" +
                    f"\n{self.bot.RED}==> {error}{self.bot.RESET}")
                return False

    def mdb_add(self, user, voluntary=False, end_date=None, prolong=True):
        """Add a new user to the mutes database."""
        is_member = isinstance(user, discord.Member)
        if not is_member:
            # This should never happen, no point in even logging it.
            raise TypeError(f"Expected discord.Member, got {type(user)}")

        uid = user.id
        server = user.guild.id
        servername = user.guild.name
        name = f"{user.name}#{user.discriminator}"
        error = None
        until = str()    # this string is filled in if called with an end_date
        duration = str() # this string too

        current_mute = self.mdb_fetch(user)
        is_muted = len(current_mute) != 0
        if is_muted: self.mdb_del(user) # Always delete existing mutes

        if is_muted and end_date != None and prolong:
            old_until = current_mute[0].until
            if old_until != None: # if current mute is permanent just replace it with a timed one
                diff = end_date - datetime.datetime.now()
                end_date = old_until + diff

    
        with self.bot.db_connect(self.mdbname) as conn:
            c = conn.cursor()
            if end_date != None:
                # Collect time info in string format for the log
                until = self.bot.db_time(end_date)
                until = f"\n{self.bot.GREEN}==> Until: {until} {self.bot.RESET}"

                duration = end_date - datetime.datetime.now()
                duration = self.bot.parse_timedelta(duration)
                duration = f"{self.bot.YELLOW}(in {duration}){self.bot.RESET}"

                end_date = self.bot.db_time(end_date) # Turn datetime object into string

                sql = f"INSERT INTO {self.mdbname}(id, server, voluntary, until) VALUES(?,?,?,?)"

                try:                    c.execute(sql, (uid, server, voluntary, end_date))
                except Exception as e:  error = e
    
            elif end_date == None:
                sql = f"INSERT INTO {self.mdbname}(id, server, voluntary) VALUES(?,?,?)"
                try:                    c.execute(sql, (uid, server, voluntary))
                except Exception as e:  error = e
    
        if error == None:
            print(f"{self.bot.current_time()} {self.bot.GREEN_B}Mutes DB:{self.bot.CYAN} added user to DB: " +
                    f"{self.bot.CYAN_B}{name} @ {servername}{self.bot.CYAN}.{self.bot.RESET}{until}{duration}")
            return True
    
        else:
            print(f"{self.bot.current_time()} {self.bot.RED_B}Mutes DB:{self.bot.CYAN} failed adding to DB: " +
                    f"{self.bot.CYAN_B}{name} @ {servername}{self.bot.CYAN}:" +
                    f"\n{self.bot.RED}==> {error}{self.bot.RESET}")
            return False

    def mdb_fetch(self, in_data):
        """If input is a server, return a list of all users from that server in the database.
        If input is a member, return what we've got on that member."""
        is_member = isinstance(in_data, discord.Member)
        is_server = isinstance(in_data, discord.Guild)

        if not is_member and not is_server:
            # This should never happen, no point in even logging it.
            raise TypeError(f"Expected discord.Member or discord.Guild, got {type(in_data)}")

        with self.bot.db_connect(self.mdbname) as conn:
            c = conn.cursor()
            fetch_id = in_data.id
            if is_member:
                server = in_data.guild
                sql = f' SELECT * FROM {self.mdbname} WHERE id = ? AND server = ? '
                c.execute(sql, (fetch_id, server.id))

            elif is_server:
                server = in_data
                sql = f' SELECT * FROM {self.mdbname} WHERE server = ? '
                c.execute(sql, (fetch_id,))
            
            output = [
                self.BanishTuple(
                    member = discord.utils.get(server.members, id=int(entry[0])),
                    voluntary = bool(entry[2]),
                    until = self.bot.db_time(entry[3])
                )
                for entry in c.fetchall()
            ]

        return output

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

