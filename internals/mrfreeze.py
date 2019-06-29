import discord                      # Required for some basic discord functionality
from discord.ext import commands    # Required for the bot class
import datetime                     # Required for current_time() and db_time()
import asyncio                      # Required for adding asynchronous loops
import sqlite3                      # Required for database stuff
from collections import namedtuple  # Required for the ServerTuple

# Importing MrFreeze submodules 
from .server_settings import *
from .path import *
from .time import *
from .colors import *
from .greeting import *

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

        # Setting up imported functions
        self.extract_time = extract_time
        self.parse_timedelta = parse_timedelta

        # Initialize bot colors
        create_colors(self)

        # Dict in which to save the ServerTuple for each server.
        self.ServerTuple = namedtuple('ServerTuple', ['trash', 'mute_channel', 'mute_role'])
        self.servertuples = dict()

        # Check that the necessary directories exist and are directories, otherwise create them.
        # All paths are relative to the working directory.
        self.db_prefix = 'databases/dbfiles'
        path_setup(self, self.db_prefix, "DB prefix")

        self.servers_prefix = 'config/servers'
        path_setup(self, self.servers_prefix, "Servers prefix")

    async def on_ready(self):
        # Set tuples up for all servers
        for server in self.guilds:
            await self.server_tuple(server)

        # Greeting (printed to console)
        bot_greeting(self)
        color_test(self)

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
        return read_server_setting(self, server, setting)

    def write_server_setting(self, server, setting, content):
        """Writes content to self.servers_prefix/server.id/setting"""
        return write_server_setting(self, server, setting, content)

    def create_server_settings(self, server):
        """Creates the directory in which server settings are stored."""
        return create_server_settings(self, server)

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
        """Good time stamps for consistent console messages throughout the bot."""
        current_time = datetime.datetime.now()
        formated_time = datetime.datetime.strftime(current_time, '%Y-%m-%d %H:%M')
        return f"{self.CYAN_B}{formated_time}{self.RESET}"
