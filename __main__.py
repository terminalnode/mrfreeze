from internals import mrfreeze  # The bot class itself
import traceback                # Debugging loading of cogs
import sys                      # Printing to stderr, exiting etc

# Instantiate the bot.
bot = mrfreeze.MrFreeze(command_prefix=["!"])

# Loading all the cogs.
# One line for each cog makes it easy to disable.
load_cogs = [
    # Silent(ish) bot functions.
    "cogs.command_log",         # Logs all executed commands.
    "cogs.inkcyclopedia",       # Listen for inkzzz.
    "cogs.error_handling",      # How the bot deals with errors.
    "cogs.temp_converter",      # How the bot deals with messages.
    "cogs.departures",          # How the bot deals with departures.
    "cogs.pin_handling",        # How the bot handles pins.
    # Mostly for owner/mods
    "cogs.maintenance",         # Owner-only commands
    "cogs.moderation",          # Mod-only commands.
    "cogs.banish.banish",       # Banish command.
    # Functions directed towards regular users.
    "cogs.user_cmds",           # Various smaller commands: !vote, !mrfreeze
    "cogs.about",               # !dummies, !readme, !source
]

# Actual loading of cogs take place here.
if __name__ == "__main__":
    for cog in load_cogs:
        try:
            bot.load_extension(cog)
        except Exception:
            print(f"Failed to load extension {cog}.", file=sys.stderr)
            traceback.print_exc()


# Run the bot
# Client.run with the bots token
# Place your token in a file called 'token'
# Put the file in the same directory as the bot.
try:
    token = open("token", "r").read().strip()
    bot.run(token, bot=True, reconnect=True)
except Exception:
    print("""\nERROR: BOT TOKEN MISSING!
Please put your bot's token in a separate text file \
called "token".\nThis file should be located in the \
same directory as the bot files.""")
    sys.exit(0)
