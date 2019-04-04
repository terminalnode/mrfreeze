# This function creates and updates a dict of the number of
# pins in every channel of the server. The dict is used to
# determine whether a pin was added or removed when the event
# on_guild_channel_pins_update triggers.

import discord

async def create_dict(botguilds):
    pinsDict = dict()
    for guild in botguilds:
        pinsDict[guild.id] = dict()
        for channel in guild.channels:
            if isinstance(channel, discord.channel.TextChannel):
                try:
                    pinsDict[guild.id][channel.id] = len(await channel.pins())
                    name = '\033[31;1m{} \033[32m#{}'.format(guild.name, channel.name)
                    print ('\033[0;36m' + 'Fetched pins from {}\033[0m'.format(name))

                    # This is for debugging purposes because the dict takes
                    # forever to build.
                    if channel.id == 466241532458958850 and len(botguilds) == 1:
                        print ('\033[36;1m' + 'PinsDict all done!' + '\033[0m')
                        return pinsDict

                except:
                    pass # Channel probably got deleted.
    print ('\033[36;1m' + 'PinsDict all done!' + '\033[0m')
    return pinsDict
