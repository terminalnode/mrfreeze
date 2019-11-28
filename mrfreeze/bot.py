import discord                      # Required for basic discord functionality
from discord.ext import commands    # Required for the bot class
import datetime                     # Required for current_time() and db_time()
from typing import NamedTuple
from typing import Optional
from discord import TextChannel
from discord import Guild

# Importing MrFreeze submodules
from mrfreeze import time, server_settings, dbfunctions
from mrfreeze import colors, paths, greeting


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
    def __init__(self, *args, **kwargs):
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

        # Initialize bot colors
        colors.create_colors(self)

        # Dict in which to save the ServerTuple for each server.
        self.servertuples = dict()

        # Check that the necessary directories exist and
        # are directories, otherwise create them.
        # All paths are relative to the working directory.
        self.db_prefix = "databases"
        paths.path_setup(self, self.db_prefix, "DB prefix")

        self.servers_prefix = "config/servers"
        paths.path_setup(self, self.servers_prefix, "Servers prefix")

    async def on_ready(self):
        # Set tuples up for all servers
        for server in self.guilds:
            await self.server_tuple(server)

        # Greeting (printed to console)
        greeting.bot_greeting(self)
        colors.color_test(self)

        # Set activity to "Listening to your commands"
        await self.change_presence(
            status=None,
            activity=discord.Activity(
                name='your commands...',
                type=discord.ActivityType.listening
                )
        )

        # Signal to the terminal that the bot is ready.
        print(f"{self.WHITE_B}READY WHEN YOU ARE CAP'N!{self.RESET}\n")

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
        return f"{self.CYAN_B}{formated_time}{self.RESET}"
