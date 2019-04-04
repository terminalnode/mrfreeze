import discord
from discord.ext import commands
import collections, random, signal
import traceback, sys, asyncio

# Importing commands from ./botfunctions
from botfunctions import *

# Instantiate the bot.
bot = mrfreeze.MrFreezeClient(command_prefix='!')

# Loading all the cogs.
# One line for each cog makes it easy to disable.
load_cogs = [   # Mostly for owner/mods.
                'cogs.maintenance',    # Owner-only commands
                'cogs.moderation',     # Mod-only commands.
                'cogs.about',          # !dummies, !readme, !source

                # Functions directed towards regular users.
                'cogs.quotes',         # !quote
                'cogs.user_cmds',      # Various smaller commands: !vote, !mrfreeze

                # Silent(ish) bot functions.
                'cogs.inkcyclopedia',      # Listen for inkzzz.
                'cogs.error_handling',     # How the bot deals with errors.
                'cogs.message_handling',   # How the bot deals with messages.
                'cogs.departure_handling', # How the bot deals with departures.
                'cogs.pin_handling',       # How the bot handles pins.
]

# Actual loading of cogs take place here.
if __name__ == '__main__':
    for cog in load_cogs:
        try:
            bot.load_extension(cog)
        except Exception as e:
            print(f'Failed to load extension {cog}.', file=sys.stderr)
            traceback.print_exc()

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
