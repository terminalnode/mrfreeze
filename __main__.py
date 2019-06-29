from internals import mrfreeze  # The bot class itself
import traceback                # Debugging loading of cogs
import sys                      # Printing to stderr, exiting etc
import signal                   # Intercepting Ctrl+C for a clean-ish exit

# Instantiate the bot.
bot = mrfreeze.MrFreeze(command_prefix=['!'])

# Loading all the cogs.
# One line for each cog makes it easy to disable.
load_cogs = [
    # Silent(ish) bot functions.
    'cogs.command_log',         # Logs all executed commands so you don't have to (as much).
    'cogs.inkcyclopedia',       # Listen for inkzzz.
    'cogs.error_handling',      # How the bot deals with errors.
    'cogs.temp_converter',      # How the bot deals with messages.
    'cogs.departures',          # How the bot deals with departures.
    'cogs.pin_handling',        # How the bot handles pins.
    # Mostly for owner/mods
    'cogs.maintenance',         # Owner-only commands
    'cogs.moderation',          # Mod-only commands.
    'cogs.banish.banish',       # Banish command.
    # Functions directed towards regular users.
    'cogs.user_cmds',           # Various smaller commands: !vote, !mrfreeze
    'cogs.about',               # !dummies, !readme, !source
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

# Graceful-ish exit
# For some reason we need two or more ctrl+c to exit, but whatever
def signal_handler(sig, frame):
        print('\n\nYou pressed Ctrl+C!\nI will now do like the tree, and get the hell out of here.')
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.pause()
