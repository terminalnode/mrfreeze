import discord, asyncio
from discord.ext import commands
from botfunctions import userdb
from botfunctions import native
from botfunctions import pinlist

class MrFreezeClient(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Background task manager
        self.bg_task = self.loop.create_task(self.bg_task_manager())

    async def on_ready(self):
        # Escape sequences:
        # 0 reset, 1 bold, 36 cyan
        print('\033[36;1m' + 'We have logged in as {0.user}'.format(self))
        print('\033[0;36m' + 'User name:           \033[1m{}'.format(self.user.name))
        print('\033[0;36m' + 'User ID:             \033[1m{}'.format(self.user.id))
        print('\033[0;36m' + 'Number of servers:   \033[1m{}'.format(len(self.guilds)))
        print('\033[0;36m' + 'Number of users:     \033[1m{}'.format(len(self.users)))
        print('\033[0m')

        # Making sure that the userdb exists.
        userdb.create()

        # Creating dict of all pins in channels in the guilds.
        # pinsDict is first set to None so we know that it's not done
        # if there's a pin made while the bot is loading.
        global pinsDict
        pinsDict = None
        pinsDict = await pinlist.create_dict(self.guilds)

        # Greetings message for all the servers now that all is setup.
        # This has been disabled due to being annoying as fuck.
        # Replaced with writing a single line to the terminal instead.
        print('\033[37;1m\n' + 'READY WHEN YOU ARE CAP\'N!' + '\033[0m')
        #
        # for i in bot.guilds:
        #     try:
        #         bot_trash = discord.utils.get(i.channels, name='bot-trash')
        #         await bot_trash.send(':wave: ' + native.mrfreeze())
        #     except:
        #         print ('ERROR: No channel bot-trash in ' + str(i.name) + '. Can\'t greet them.')

        # Set activity to "Listening to your commands"
        await self.change_presence(status=None, activity=
            discord.Activity(name='your commands...', type=discord.ActivityType.listening))


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
                        replystr = 'It\'s with great regreat that I need to inform y\'all that the exile of %s has come to an end.'
                        await bot_trash.send(replystr % (unmuted_mentions,))
                    else:
                        print ('There is no bot-trash.')
