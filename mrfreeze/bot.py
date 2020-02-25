import datetime
import os
import sys
from typing import NamedTuple
from typing import Optional

import discord
from discord import Guild
from discord import TextChannel
from discord.ext import commands

# Importing MrFreeze submodules
from mrfreeze import colors, greeting, paths
from mrfreeze import dbfunctions, server_settings, time


# Usage note!
# The bot supports adding periodic asynchronous checks through
# the function add_bg_task(task, name).
# task is the function (see below) you wish to add.
# name is just some string that's not very important but necessary nontheless.
#
# A basic check looks something like this:
# async def name(self, args):
#     await self.bot.wait_until_ready()
#     while not self.bot.is_closed():
#         await asyncio.sleep(NUMBER)
#         pass # Do stuff on loop
class ServerTuple(NamedTuple):
    trash:        str
    mute_channel: str
    mute_role:    str


class MrFreeze(commands.Bot):
    def __init__(self, settingsdb="server_settings", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_tasks = dict()  # Background task manager

        # Setting up imported functions so they can be accessed by all cogs
        self.extract_time = time.extract_time
        self.parse_timedelta = time.parse_timedelta
        self.read_server_setting = server_settings.read_server_setting
        self.write_server_setting = server_settings.write_server_setting
        self.create_server_settings = server_settings.create_server_settings
        self.db_connect = dbfunctions.db_connect
        self.db_create = dbfunctions.db_create
        self.db_time = dbfunctions.db_time

        # Dict in which to save the ServerTuple for each server.
        self.servertuples = dict()

        # Check that the necessary directories exist and
        # are directories, otherwise create them.
        # All paths are relative to the working directory.
        self.db_prefix = "databases"
        paths.path_setup(self.db_prefix, "DB prefix")

        self.servers_prefix = "config/servers"
        paths.path_setup(self.servers_prefix, "Servers prefix")

        # Server settings database creation
        self.settingsdb = settingsdb
        self.trash_channels = "trash_channels"
        self.mute_channels  = "mute_channels"
        self.mute_roles     = "mute_roles"
        # Complete list of tables and their rows in the server settings database.
        # Primary key(s) is marked with an asterisk (*).
        # Mandatory but not primary keys are marked with a pling (!).
        # TABLE                 ROWS       TYPE     FUNCTION
        # self.trash_channels   channel*   integer  Channel ID
        #                       server*    integer  Server ID
        #
        # self.mute_channels    channel*   integer  Channel ID
        #                       server*    integer  Server ID
        #
        # self.mute_roles       role*      integer  Channel ID
        #                       server*    integer  Server ID
        trash_chan_tbl = f"""
        CREATE TABLE IF NOT EXISTS {self.trash_channels} (
            channel     integer NOT NULL,
            server         integer NOT NULL,
            CONSTRAINT server_trash_channel PRIMARY KEY (channel, server)
        );"""

        mute_chan_tbl = f"""
        CREATE TABLE IF NOT EXISTS {self.mute_channels} (
            channel     integer NOT NULL,
            server      integer NOT NULL,
            CONSTRAINT server_mute_channel PRIMARY KEY (channel, server)
        );"""

        mute_role_tbl = f"""
        CREATE TABLE IF NOT EXISTS {self.mute_channels} (
            role        integer NOT NULL,
            server      integer NOT NULL,
            CONSTRAINT server_mute_role PRIMARY KEY (role, server)
        );"""

        self.db_create(self, self.settingsdb, trash_chan_tbl, comment="trash channels table")
        self.db_create(self, self.settingsdb, mute_chan_tbl, comment="mute channels table")
        self.db_create(self, self.settingsdb, mute_role_tbl, comment="mute roles table")

    async def on_ready(self):
        # Set tuples up for all servers
        for server in self.guilds:
            await self.server_tuple(server)

        # Greeting (printed to console)
        greeting.bot_greeting(self)
        colors.color_test()

        # Set activity to "Listening to your commands"
        await self.change_presence(
            status=None,
            activity=discord.Activity(
                name='your commands...',
                type=discord.ActivityType.listening
                )
        )

        # Signal to the terminal that the bot is ready.
        print(f"{colors.WHITE_B}READY WHEN YOU ARE CAP'N!{colors.RESET}\n")

    def path_setup(self, path, trivial_name):
        """Create various directories which the bot needs."""
        if os.path.isdir(path):
            print(f"{colors.GREEN_B}{trivial_name} {colors.GREEN}({path}) " +
                  f"{colors.CYAN}exists and is a directory.{colors.RESET}")
        elif os.path.exists(path):
            print(f"{colors.RED_B}{trivial_name} {colors.RED}({path}) " +
                  f"{colors.CYAN}exists but is not a directory. " +
                  f"Aborting.{colors.RESET}")
            sys.exit(0)
        else:
            try:
                os.makedirs(path)
                print(f"{colors.GREEN_B}{trivial_name} " +
                      f"{colors.GREEN}({path}){colors.CYAN} was " +
                      f"successfully created.{colors.RESET}")
            except Exception as e:
                print(f"{colors.RED_B}{trivial_name} {colors.RED}({path}) " +
                      f"{colors.CYAN} does not exist and could not be " +
                      f"created:\n{colors.RED}==> {e}{colors.RESET}")
                sys.exit(0)

    async def server_tuple(self, server):
        self.servertuples[server.id] = ServerTuple(
            self.get_trash_channel(server),
            self.get_mute_channel(server),
            self.get_mute_role(server)
        )

    # Various utility functions universal to the bot.
    # Most of these are copied from internals/*.py so
    # cogs won't have to import so much stuff.
    def add_bg_task(self, task, name):
        """
        Add a task to run in the background in the bot.
        Useful for periodic checks/updates.
        """
        self.bg_tasks[name] = self.loop.create_task(task)

    def get_trash_channel(self, guild: Guild) -> Optional[TextChannel]:
        """
        Currently just gives the channel with the name bot-trash.
        In the future this may be expanded so servers can designate whatever
        channel they want as Trash.
        """
        for channel in guild.text_channels:
            if channel.name.lower() == "bot-trash":
                return channel
        return None

    def get_mute_channel(self, guild: Guild):
        """
        Currently just gives the channel with the name antarctica.
        In the future this may be expanded so servers can designate whatever
        channel they want as Antarctica.
        """
        for channel in guild.text_channels:
            if channel.name.lower() == "antarctica":
                return channel
        return None

    def set_mute_channel(self, guild: Guild):
        """
        Set the mute channel for a given server.
        """
        pass

    def get_mute_role(self, guild: Guild):
        """
        Currently just gives the role with the name Antarctica.
        In the future this may be expanded so servers can designate whatever
        role they want as Antarctica.
        """
        for role in guild.roles:
            if role.name.lower() == "antarctica":
                return role
        return None

    def mentions_list(self, mentions):
        """
        Create a string of mentions from a list of user objects.
        """
        mentions = [user.mention for user in mentions]
        if len(mentions) == 0:
            return "No one"
        elif len(mentions) == 1:
            return mentions[0]
        else:
            return ", ".join(mentions[:-1]) + f" and {mentions[-1]}"

    def current_time(self):
        """
        Good time stamps for consistent console messages throughout the bot.
        """
        formated_time = datetime.datetime.strftime(
                datetime.datetime.now(),
                "%Y-%m-%d %H:%M"
        )
        return f"{colors.CYAN_B}{formated_time}{colors.RESET}"
