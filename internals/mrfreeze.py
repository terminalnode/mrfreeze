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
        greeting = list()
        greeting.append(f'{var.cyan}{var.boldcyan}We have logged in as {self.user}')
        greeting.append(f'{var.cyan}User name:           {var.boldcyan}{self.user.name}')
        greeting.append(f'{var.cyan}User ID:             {var.boldcyan}{self.user.id}')
        greeting.append(f'{var.cyan}Number of servers:   {var.boldcyan}{len(self.guilds)}')
        greeting.append(f'{var.cyan}Number of channels:  {var.boldcyan}{sum([ len(guild.text_channels) for guild in self.guilds ])}')
        greeting.append(f'{var.cyan}Number of users:     {var.boldcyan}{len(self.users)}')

        # Calculating box width...
        # Each escape character takes up 8 spaces.
        # We then need two extra characters on each side.
        longest = max(greeting, key=lambda x: len(x)-16)
        linewidth = (len(longest) - 16)
        box = f"{var.cyan}#{var.reset}"

        print(f"{ box * (linewidth + 4) }")
        for line in greeting:
            width = ( len(line) - 16 )
            line += ( ' ' * (linewidth - width) )
            print(f"{box} {line} {box}")
        print(f"{ box * (linewidth + 4) }\n")


        # Making sure that the userdb exists.
        # userdb.create()   # This is being replaced.
        regionbl.create()
        mutes.create()

        # Set activity to "Listening to your commands"
        await self.change_presence(status=None, activity=
            discord.Activity(name='your commands...', type=discord.ActivityType.listening))

        # Signal to the terminal that the bot is ready.
        print(f'{var.boldwhite}\nREADY WHEN YOU ARE CAP\'N!{var.reset}')
