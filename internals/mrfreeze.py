import discord, asyncio
from discord.ext import commands
from databases import mutes, regionbl
from internals import var, native # Colors

class MrFreeze(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Background task manager
        self.bg_tasks = dict()

    def add_bg_task(self, task, name):
        """Add a task to run in the background in the bot.
        Useful for periodic checks/updates."""
        # BASIC BACKGROUND FUNCTION TEMPLATE:
        # async def name(self, args):
        # await self.bot.wait_until_ready()
        # while not self.bot.is_closed():
        #    await asyncio.sleep(NUMBER)
        self.bg_tasks[name] = self.loop.create_task(task)

    async def on_ready(self):
        print(f'{var.boldcyan}We have logged in as {self.user}')
        print(f'{var.cyan}User name:           {var.boldcyan}{self.user.name}')
        print(f'{var.cyan}User ID:             {var.boldcyan}{self.user.id}')
        print(f'{var.cyan}Number of servers:   {var.boldcyan}{len(self.guilds)}')
        print(f'{var.cyan}Number of users:     {var.boldcyan}{len(self.users)}{var.reset}')

        # Making sure that the userdb exists.
        # userdb.create()   # This is being replaced.
        regionbl.create()
        mutes.create()

        # Set activity to "Listening to your commands"
        await self.change_presence(status=None, activity=
            discord.Activity(name='your commands...', type=discord.ActivityType.listening))

        # Signal to the terminal that the bot is ready.
        print(f'{var.boldwhite}\nREADY WHEN YOU ARE CAP\'N!{var.reset}')
