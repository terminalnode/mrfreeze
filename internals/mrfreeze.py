import discord, asyncio
from discord.ext import commands
from botfunctions import native
from databases import mutes, regionbl
from internals import var # Colors

class MrFreeze(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Background task manager
        self.bg_task = self.loop.create_task(self.bg_task_manager())

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

    async def bg_task_manager(self):
        await self.wait_until_ready()

        channel = self.get_channel(466241532458958850)
        while not self.is_closed():
            await asyncio.sleep(15)

            # First we fix mutes.
            mute_status = userdb.list_mute()
            for guild in self.guilds:
                unmuted = list()
                not_unmuted = list()

                # Check that there's an antarctica role, otherwise set it to None.
                try:
                    antarctica_role = discord.utils.get(guild.roles, name='Antarctica')
                except:
                    antarctica_role = None

                # Check that there's a bot-trash channel, otherwise set it to None.
                try:
                    bot_trash = discord.utils.get(guild.channels, name='bot-trash')
                except:
                    bot_trash = None

                # Go through all the entries in mute_status.
                for entry in mute_status:
                    if entry['server'] == guild.id:
                        user = discord.utils.get(guild.members, id=entry['user'])

                        # If the user doesn't have the antarctica role (i.e. manually deleted)
                        # we'll just delete the database entry silently.
                        if antarctica_role and not (antarctica_role in user.roles):
                            userdb.fix_mute(user, delete=True)

                        # If the user does have the antarctica role and entry['time'] is
                        # true, we will try to delete the role and add them to the list
                        # of successfully unmuted people. Then we'll delete the db entry.
                        elif antarctica_role and entry['time']:
                            try:
                                await user.remove_roles(antarctica_role, reason='Time, the sentence is served.')
                                unmuted.append(user)
                                userdb.fix_mute(user, delete=True)
                            except:
                                pass
                                # not_unmuted.append(user)

                if (len(unmuted) + len(not_unmuted)) > 0:
                    unmuted_mentions = native.mentions_list(unmuted)

                    # Currently these actually aren't used because I'm not sure where to put them.
                    # not_unmuted_mentions = native.mentions_list(not_unmuted)

                    if bot_trash != None:
                        try:
                            await bot_trash.send(f"It's with great regreat that I need to inform y'all that the exile of {unmuted_mentions} has come to an end.")
                        except Exception as e:
                            print(f"{var.cyan}Can't post unbanished notification: {var.red}{e}{var.reset}")
                    else:
                        print (f"{var.cyan}Can't post unbanished notification: {var.red}There is no bot-trash.{var.reset}")
