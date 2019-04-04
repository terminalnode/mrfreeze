import discord
from discord.ext import commands
import collections, random, signal
import traceback, sys, asyncio

# Importing commands from ./botfunctions
from botfunctions import *

# Starting the bot, then removing help command
# because we're going to implement our own help.
bot = mrfreeze.MrFreezeClient(command_prefix='!')

# Cogs starting with cmd contains only one command,
# Cogs starting with cmds has multiple commands sharing some common trait.
load_cogs = [ 'cogs.maintenance',    # Owner-only commands
              'cogs.moderation',     # Mod-only commands.
              'cogs.about',          # !dummies, !readme, !source
              'cogs.quotes',         # !quote
              'cogs.user_cmds',      # Various smaller commands: !rules, !vote, !mrfreeze
              'cogs.inkcyclopedia',  # Listen for inkzzz.

              # Silent(ish) bot functions.
              'cogs.error_handling',     # How the bot deals with errors.
              'cogs.message_handling',   # How the bot deals with messages.
              'cogs.departure_handling', # How the bot deals with departures
              ]

# Here's where the actual loading of the cogs go.
if __name__ == '__main__':
    for cog in load_cogs:
        try:
            bot.load_extension(cog)
        except Exception as e:
            print(f'Failed to load extension {cog}.', file=sys.stderr)
            traceback.print_exc()


# A message was pinned.
@bot.event
async def on_guild_channel_pins_update(channel, last_pin):
    global pinsDict

    # Unfortunately we have to cast an empty return
    # if the dict isn't finished yet.
    if pinsDict == None:
        print ('The PinsDict isn\'t finished yet!')
        return

    # The channel might be new, if so we need to create an entry for it.
    try:
        pinsDict[channel.guild.id][channel.id]
    except KeyError:
        pinsDict[channel.guild.id][channel.id] = 0

    # For comparisson between the two. These numbers will be
    # used to determine whether a pin was added or removed.
    channel_pins = await channel.pins()
    old_pins = pinsDict[channel.guild.id][channel.id]
    new_pins = len(channel_pins)

    # Was a new pin added?
    # If a pin was added when the bot was starting up, this won't work.
    # But it will work the next time as the pinsDict is updated.
    was_added = False
    if new_pins > old_pins:
        was_added = True

    # Updating the list of pins.
    pinsDict[channel.guild.id][channel.id] = new_pins

    if was_added:
        message = channel_pins[0]
        pinned_message = discord.Embed(description = message.content, color=0x00dee9)
        pinned_message.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)

        # Attaching first attachment of the post, if there are any.
        if message.attachments:
            pinned_message.set_image(url=message.attachments[0].url)

        channel_history = message.channel.history(limit=10)
        for i in range(10):
            sys_msg = await channel_history.next()
            if isinstance(sys_msg.type, type(discord.MessageType.pins_add)):
                author = sys_msg.author.mention # This is the person who pinned the message.
                await sys_msg.delete()
                break # No need to look further.

        replystr = 'The following message was just pinned by %s:\n'
        await channel.send(replystr % (author), embed=pinned_message)



### Program ends here
# Client.run with the bots token
# Place your token in a file called 'token'
# Put the file in the same directory as the bot.
try:
    token = open('token', 'r').read().strip()
    bot.run(token, bot=True, reconnect=True)
except:
    print ('\nERROR: BOT TOKEN MISSING\n' +
           'Please put your bot\'s token in a separate text file called \'token\'.\n' +
           'This file should be located in the same directory as the bot files.\n')
    sys.exit(0)

# Graceful exit
def signal_handler(sig, frame):
        print('\n\nYou pressed Ctrl+C!\nI will now do like the tree, and get out of here.')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.pause()
