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
class MuteStr(Enum):
    # Gag mutes
    SELF_FREEZE_MUTE    = auto()
    FREEZE_MUTE         = auto()
    SELF_MUTE_MOD       = auto()
    SELF_MUTE_USER      = auto()
    NON_MOD_MUTE        = auto()
    # User mutes
    MISSING_MUTE        = auto()
    SINGLE_MUTE         = auto()
    MULTI_MUTE          = auto()
    SINGLE_MUTE_FAIL    = auto()
    MULTI_MUTE_FAIL     = auto()
    # Generic
    PAST_TENSE          = auto()

templates = dict()
templates['mute'] = {
    # Gag mutes
    MuteStr.SELF_FREEZE_MUTE    : Template("$author You can't silence me! Much less yourself. :rage:"),
    MuteStr.FREEZE_MUTE         : Template("$author If you want me to be silent maybe stop calling on me? Just a thought."),
    MuteStr.SELF_MUTE_MOD       : Template("$author Trust me, if I could I would."),
    MuteStr.SELF_MUTE_USER      : Template("$author PLACEHOLDER **[mute]** self-mute-user"),
    MuteStr.NON_MOD_MUTE        : Template("$author PLACEHOLDER **[mute]** non-mod-mute"),
    # User mutes
    MuteStr.MISSING_MUTE        : Template("$author Uhh, who exactly is it that you want me to mute?"),
    MuteStr.SINGLE_MUTE         : Template("$victim has been muted for $time."),
    MuteStr.MULTI_MUTE          : Template("$victim have been muted for $time."),
    MuteStr.SINGLE_MUTE_FAIL    : Template("$victim $error"),
    MuteStr.MULTI_MUTE_FAIL     : Template("$victim $error"),
    # Generic
    MuteStr.PAST_TENSE          : "muted",
}

templates['banish'] = {
    # Gag mutes
    MuteStr.SELF_FREEZE_MUTE    : Template("$author PLACEHOLDER **[banish]** self-freeze-mute"),
    MuteStr.FREEZE_MUTE         : Template("$author PLACEHOLDER **[banish]** freeze-mute"),
    MuteStr.SELF_MUTE_MOD       : Template("$author PLACEHOLDER **[banish]** self-mute-mod"),
    MuteStr.SELF_MUTE_USER      : Template("$author PLACEHOLDER **[banish]** self-mute-user"),
    MuteStr.NON_MOD_MUTE        : Template("$author PLACEHOLDER **[banish]** non-mod-mute"),
    # User mutes
    MuteStr.MISSING_MUTE        : Template("$author PLACEHOLDER **[banish]** missing-mute"),
    MuteStr.SINGLE_MUTE         : Template("$author PLACEHOLDER **[banish]** single-mute"),
    MuteStr.MULTI_MUTE          : Template("$author PLACEHOLDER **[banish]** multi-mute"),
    MuteStr.SINGLE_MUTE_FAIL    : Template("$author PLACEHOLDER **[banish]** single-mute-failed"),
    MuteStr.MULTI_MUTE_FAIL     : Template("$author PLACEHOLDER **[banish]** multi-mute-failed"),
    # Generic
    MuteStr.PAST_TENSE          : "banished",
}

templates['hogtie'] = {
    # Gag mute
    MuteStr.SELF_FREEZE_MUTE    : Template("$author PLACEHOLDER **[hogtie]** self-freeze-mute"),
    MuteStr.FREEZE_MUTE         : Template("$author PLACEHOLDER **[hogtie]** freeze-mute"),
    MuteStr.SELF_MUTE_MOD       : Template("$author PLACEHOLDER **[hogtie]** self-mute-mod"),
    MuteStr.SELF_MUTE_USER      : Template("$author PLACEHOLDER **[hogtie]** self-mute-user"),
    MuteStr.NON_MOD_MUTE        : Template("$author PLACEHOLDER **[hogtie]** non-mod-mute"),
    # User mutes
    MuteStr.MISSING_MUTE        : Template("$author PLACEHOLDER **[hogtie]** missing-mute"),
    MuteStr.SINGLE_MUTE         : Template("$author PLACEHOLDER **[hogtie]** single-mute"),
    MuteStr.MULTI_MUTE          : Template("$author PLACEHOLDER **[hogtie]** multi-mute"),
    MuteStr.SINGLE_MUTE_FAIL    : Template("$author PLACEHOLDER **[hogtie]** single-mute-failed"),
    MuteStr.MULTI_MUTE_FAIL     : Template("$author PLACEHOLDER **[hogtie]** multi-mute-failed"),
    # Generic
    MuteStr.PAST_TENSE          : "hogtied"
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
        print("banish")

    @_banish.error
    async def _banish_error(self, ctx, error):
        if not isinstance(error, discord.ext.commands.CheckFailure):
            # Only run this on Check Failure.
            return

        await ctx.send("special banish error")

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

    def mdb_add(self, user, voluntary=False, end_date=None, prolong=False):
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

                try:
                    c.execute(sql, (uid, server, voluntary, end_date))
                except Exception as e:
                    error = e
    
            elif end_date == None:

                sql = f"INSERT INTO {self.mdbname}(id, server, voluntary) VALUES(?,?,?)"
                try:
                    c.execute(sql, (uid, server, voluntary))
                except Exception as e:
                    error = e
    
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

