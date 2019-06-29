import discord                      # Required for some basic discord functionality
from discord.ext import commands    # Required for the bot class
import datetime                     # Required for bot.current_time() and db_time()
import asyncio                      # Required for adding asynchronous loops
import sqlite3                      # Required for database stuff
import os                           # Required for creation of folders and reading of files
import sys                          # Required for exiting when necessary files can't be created.
import re                           # Required for extract_time()
from collections import namedtuple  # Required for the ServerTuple

# Usage note!
# The bot supports adding periodic asynchronous checks through the function add_bg_task(task, name).
# task is the function (see below) you wish to add.
# name is just some string that's not very important but necessary nontheless.
#
# A basic check looks something like this:
# async def name(self, args):
#     await self.bot.wait_until_ready()
#     while not self.bot.is_closed():
#         await asyncio.sleep(NUMBER)
#         pass # Do stuff on loop

class MrFreeze(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_tasks = dict() # Background task manager

        # Colors codes to easily colorise output throughout the bot.
        self.BLACK,   self.BLACK_B      = '\033[00;30m', '\033[30;01m'
        self.RED,     self.RED_B        = '\033[00;31m', '\033[31;01m'
        self.GREEN,   self.GREEN_B      = '\033[00;32m', '\033[32;01m'
        self.YELLOW,  self.YELLOW_B     = '\033[00;33m', '\033[33;01m'
        self.BLUE,    self.BLUE_B       = '\033[00;34m', '\033[34;01m'
        self.MAGENTA, self.MAGENTA_B    = '\033[00;35m', '\033[35;01m'
        self.CYAN,    self.CYAN_B       = '\033[00;36m', '\033[36;01m'
        self.WHITE,   self.WHITE_B      = '\033[00;37m', '\033[37;01m'
        self.RESET                      = '\033[00000m'

        # Dict in which to save the ServerTuple for each server.
        self.ServerTuple = namedtuple('ServerTuple', ['trash', 'mute_channel', 'mute_role'])
        self.servertuples = dict()

        # Check that the necessary directories exist and are directories, otherwise create them.
        # All paths are relative to the working directory.
        self.db_prefix = 'databases/dbfiles'
        self.path_setup(self.db_prefix, "DB prefix")

        self.servers_prefix = 'config/servers'
        self.path_setup(self.servers_prefix, "Servers prefix")
        
    def path_setup(self, path, trivial_name):
        """This is part of the setup process. Creates various directories the bot needs."""
        if os.path.isdir(path):
            print(f"{self.GREEN_B}{trivial_name} {self.GREEN}({path}) {self.CYAN}exists and is a directory.{self.RESET}")
        elif os.path.exists(path):
            print(f"{self.RED_B}{trivial_name} {self.RED}({path}) {self.CYAN}exists but is not a directory. Aborting.{self.RESET}")
            sys.exit(0)
        else:
            try:
                os.makedirs(path)
                print(f"{self.GREEN_B}{trivial_name} {self.GREEN}({path}) {self.CYAN}was successfully created.{self.RESET}")
            except Exception as e:
                print(f"{self.RED_B}{trivial_name} {self.RED}({path}) {self.CYAN} does not exist and could not be created:\n" +
                    f"{self.RED}==> {e}{self.RESET}")
                sys.exit(0)

    async def on_ready(self):
        # Set tuples up for all servers
        for server in self.guilds:
            await self.server_tuple(server)

        # Attractive greeting message with a couple of stats.
        greeting = list()
        greeting.append(f'{self.CYAN}{self.CYAN_B}We have logged in as {self.user}')
        greeting.append(f'{self.CYAN}User name:           {self.CYAN_B}{self.user.name}')
        greeting.append(f'{self.CYAN}User ID:             {self.CYAN_B}{self.user.id}')
        greeting.append(f'{self.CYAN}Number of servers:   {self.CYAN_B}{len(self.guilds)}')
        greeting.append(f'{self.CYAN}Number of channels:  {self.CYAN_B}{sum([ len(guild.text_channels) for guild in self.guilds ])}')
        greeting.append(f'{self.CYAN}Number of users:     {self.CYAN_B}{len(self.users)}')

        # Calculating box width...
        # - Each escape character takes up 8 spaces.
        # - We then need two extra characters on each side.
        longest = max(greeting, key=lambda x: len(x)-16)
        linewidth = (len(longest) - 16)
        box = f"{self.CYAN}#{self.RESET}"

        print(f"{ box * (linewidth + 4) }")
        for line in greeting:
            width = ( len(line) - 16 )
            line += ( ' ' * (linewidth - width) )
            print(f"{box} {line} {box}")
        print(f"{ box * (linewidth + 4) }")

        # Color test
        print(f"{self.CYAN_B}Color test: " +
        f"{self.BLACK}#"   + f"{self.BLACK_B}#" +
        f"{self.RED}#"     + f"{self.RED_B}#" +
        f"{self.GREEN}#"   + f"{self.GREEN_B}#" +
        f"{self.YELLOW}#"  + f"{self.YELLOW_B}#" +
        f"{self.BLUE}#"    + f"{self.BLUE_B}#" +
        f"{self.MAGENTA}#" + f"{self.MAGENTA_B}#" +
        f"{self.CYAN}#"    + f"{self.CYAN_B}#" +
        f"{self.WHITE}#"   + f"{self.WHITE_B}#" +
        f"{self.RESET}"    + " RESET")

        # Set activity to "Listening to your commands"
        await self.change_presence(status=None, activity=
            discord.Activity(name='your commands...', type=discord.ActivityType.listening))

        # Signal to the terminal that the bot is ready.
        print(f"{self.WHITE_B}READY WHEN YOU ARE CAP'N!{self.RESET}\n")

    async def server_tuple(self, server):
        self.servertuples[server.id] = self.ServerTuple(
            self.get_trash_channel(server),
            self.get_mute_channel(server),
            self.get_mute_role(server)
        )

    # Database-related utility functions
    def db_connect(self, dbname):
        """Creates a connection to the regionbl database."""
        db_file = f'{self.db_prefix}/{dbname}.db'
        conn = sqlite3.connect(db_file)
        return conn

    def db_create(self, dbname, tables):
        """Create a database file from the provided tables."""
        conn = self.db_connect(dbname)
        with conn:
            try:
                c = conn.cursor()
                c.execute(tables)
                print(f'{self.CYAN}DB created: {self.GREEN_B}{dbname}{self.RESET}')

            except sqlite3.Error as e:
                print(f'{self.CYAN}DB failure: {self.RED_B}{dbname}\n{str(e)}{self.RESET}')

    def db_time(self, in_data):
        """Pase datetime to string, string to datetime and everything else to None."""
        timeformat = "%Y-%m-%d %H:%M:%S"
    
        if isinstance(in_data, datetime.datetime):
            return datetime.datetime.strftime(in_data, timeformat)
        elif isinstance(in_data, str):
            return datetime.datetime.strptime(in_data, timeformat)
        else:
            return None

    # Various utility functions universal to the bot.
    # Most of these are copied from internals/*.py so cogs won't have to import so much stuff.
    def read_server_setting(self, server, setting):
        """Reads and returns a setting stored in self.servers_prefix/server.id/setting."""
        server_dir = self.create_server_settings(server)
        if not server_dir:
            return False

        setting_path = os.path.join(server_dir, setting)
        try:
            with open(setting_path, 'r') as f:
                return f.read().strip()
        except:
            return False

    def write_server_setting(self, server, setting, content):
        """Writes content to self.servers_prefix/server.id/setting"""
        server_dir = self.create_server_settings(server)
        if not server_dir:
            return False

        setting_path = os.path.join(server_dir, setting)
        try:
            with open(setting_path, 'w') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"{self.current_time()} {self.RED_B}Server settings:{self.CYAN} failed to write {self.YELLOW}{setting_path}{self.CYAN}:\n" +
                f"{self.RED}==> {e}{self.RESET}")
            return False

    def create_server_settings(self, server):
        """Creates the directory in which server settings are stored."""
        server_dir = os.path.join(self.servers_prefix, str(server.id))
        if not os.path.isdir(server_dir):
            if os.path.exists(server_dir):
                print(f"{self.current_time()} {self.RED_B}Server settings:{self.CYAN} path for "+
                    f"{self.CYAN_B}{server.name} {self.YELLOW}({server_dir}){self.CYAN} exists but is a file.{self.RESET}")
                return None
            else:
                try:
                    os.makedirs(server_dir)
                    print(f"{self.current_time()} {self.GREEN_B}Server settings:{self.CYAN} created dir for " +
                        f"{self.CYAN_B}{server.name} {self.YELLOW}({server_dir}){self.RESET}")
                except Exception as e:
                    print(f"{self.current_time()} {self.RED_B}Server settings:{self.CYAN} could not create dir for " +
                        f"{self.CYAN_B}{server.name} {self.YELLOW}({server_dir})\n" +
                        f"{self.RED}==> {e}{self.RESET}")
                    return None
        return server_dir

    def add_bg_task(self, task, name):
        """Add a task to run in the background in the bot.
        Useful for periodic checks/updates."""
        self.bg_tasks[name] = self.loop.create_task(task)

    def get_trash_channel(self, guild):
        """Currently just gives the channel with the name bot-trash.
        In the future this may be expanded so servers can designate whatever channel they want as Antarctica."""
        for channel in guild.text_channels:
            if channel.name.lower() == "bot-trash":
                return channel
        return None
   
    def get_mute_channel(self, guild):
        """Currently just gives the channel with the name antarctica.
        In the future this may be expanded so servers can designate whatever channel they want as Antarctica."""
        for channel in guild.text_channels:
            if channel.name.lower() == "antarctica":
                return channel
        return None

    def get_mute_role(self, guild):
        """Currently just gives the role with the name antarctica.
        In the future this may be expanded so servers can designate whatever role they want as Antarctica."""
        for role in guild.roles:
            if role.name.lower() == "antarctica":
                return role
        return None

    def mentions_list(self, mentions):
        """Create a string of mentions from a list of user objects."""
        mentions = [ user.mention for user in mentions ]
        if len(mentions) == 0:      return "No one"
        elif len(mentions) == 1:    return mentions[0]
        else:                       return ", ".join(mentions[:-1]) + f" and {mentions[-1]}"
    def current_time(self):
        """Good time stamps for errors throughout the bot."""
        current_time = datetime.datetime.now()
        return self.CYAN_B + datetime.datetime.strftime(current_time, '%Y-%m-%d %H:%M') + self.RESET

    def extract_time(self, args, fallback_minutes=True):
        """Extract time expressions from a set of arguments.
        If time expressions are not found, assume all digits refer to minutes.
    
        Return a timedelta and an end time if successful, otherwise (None, None)."""
    
        # Create regular expression
        seconds   = 'seconds?|secs?|s[, ]'
        minutes   = 'minutes?|mins?|m[, ]'
        hours     = 'hours?|hrs?|h[, ]'
        days      = 'days?|d[, ]'
        weeks     = 'weeks?|w[, ]'
        months    = 'months?|mnth?s?|mons?'
        years     = 'years?|yrs?|y[, ]'
        find_time = f"(\d+) ?(({seconds})|({minutes})|({hours})|({days})|({weeks})|({months})|({years}))"
    
        regex_output = re.findall(
                find_time,      # Use our newly created regex.
                ' '.join(args), # Search through the arguments.
                re.IGNORECASE)   # Ignore case when applying the expression.
    
        # Sum up all hits for the different time units
        time_dict = {
        'seconds' : sum( [ int(row[0]) for row in regex_output if row[2] ] ),
        'minutes' : sum( [ int(row[0]) for row in regex_output if row[3] ] ),
        'hours'   : sum( [ int(row[0]) for row in regex_output if row[4] ] ),
        'days'    : sum( [ int(row[0]) for row in regex_output if row[5] ] ),
        'weeks'   : sum( [ int(row[0]) for row in regex_output if row[6] ] ),
        'months'  : sum( [ int(row[0]) for row in regex_output if row[7] ] ),
        'years'   : sum( [ int(row[0]) for row in regex_output if row[8] ] ),
        }
    
        # Create a new datetime object based on these numbers.
        # Months and years are converted to 30 and 365 days respectively.
        add_time = datetime.timedelta(
                days    =   time_dict['days'] + (time_dict['months'] * 30) + (time_dict['years'] * 365),
                weeks   =   time_dict['weeks'],
                hours   =   time_dict['hours'],
                minutes =   time_dict['minutes'],
                seconds =   time_dict['seconds'])
        current_date = datetime.datetime.now()

        try:
            end_date = current_date + add_time
        except OverflowError:
            end_date = datetime.datetime.max
            add_time = datetime.datetime.max - current_date
    
        # If nothing was found, assume all numbers are minutes.
        if (end_date == current_date) and fallback_minutes:
            no_minutes = sum([ int(arg) for arg in args if arg.isdigit() ])
            add_time = datetime.timedelta(minutes = no_minutes)
            end_date = current_date + add_time
    
        # Return None if current date and end date are different.
        if end_date != current_date:    return add_time, end_date
        else:                           return None, None
    
    def parse_timedelta(self, time_delta):
        """Takes a timedelta object and outputs a string such as '1 day, 2 hours[...]'"""
        # This function takes a time delta as it's argument and outputs
        # a string such as "1 days, 2 hours, 3 minutes and 4 seconds".
    
        if time_delta == None:
            return "an eternity"
    
        # Time delta only gives us days and seconds, we have to calculate
        # hours and minutes ourselves.
        days = time_delta.days
        seconds = time_delta.seconds
        microseconds = time_delta.microseconds
    
        # Some simple calculations. Weeks are the last whole number we can get from
        # days/7 i.e. int(days/7), then weeks*7 are subtracted from the remanining days
        # and so on and so on for hours and minutes.
        weeks = int(days / 7)
        days = (days - (weeks * 7))
        hours = int(seconds / 3600)
        seconds = (seconds - (hours * 3600))
        minutes = int(seconds / 60)
        seconds = round((seconds - minutes * 60 + microseconds / 1000000))
    
        time_str = ''
        size_order = (
            ('week', weeks), ('day', days),
            ('hour', hours), ('minute', minutes),
            ('second', seconds)
        )
    
        for value in range(len(size_order)):
            # Number of trailing values are used to know if we should
            # add an 'and' after the value.
            trailing_values = 0
    
            # Checking that this isn't the last value.
            if value != (len(size_order) - 1):
    
                # Going through all trailing values and checking which are non-zero.
                for i in size_order[value+1:]:
                    if i[1] > 0:
                        trailing_values += 1
    
            # Adding the value to the string if it's more than zero.
            if size_order[value][1] > 0:
                if size_order[value][1] == 1:
                    time_str += str(size_order[value][1]) + ' ' + size_order[value][0]
                else:
                    time_str += str(size_order[value][1]) + ' ' + size_order[value][0] + 's'
    
                if trailing_values == 0:
                    pass
                elif trailing_values == 1:
                    time_str += ' and '
                else:
                    time_str += ', '
        return time_str
