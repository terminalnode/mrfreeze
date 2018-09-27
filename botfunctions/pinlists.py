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
                    print ('PinsDict: fetched ' + guild.name + ' #' + channel.name)

                    # This is for debugging purposes because the dict takes
                    # forever to build.
                    if channel.name == 'bot-trash':
                        return pinsDict
                        print ('PinsDict all done!')

                except:
                    pass # Channel probably got deleted.
    print ('PinsDict all done!')
    return pinsDict
