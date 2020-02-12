import discord
from mrfreeze import bot, colors
import traceback          # Debugging loading of cogs
import sys                # Printing to stderr, exiting etc

# Instantiate the bot.
bot = bot.MrFreeze(command_prefix=["!"])

# Loading all the cogs.
# One line for each cog makes it easy to disable.
load_cogs = [
    # Silent(ish) bot functions.
    "mrfreeze.cogs.command_log",
    "mrfreeze.cogs.inkcyclopedia",
    "mrfreeze.cogs.error_handling",
    "mrfreeze.cogs.temp_converter",
    "mrfreeze.cogs.departures",
    "mrfreeze.cogs.pin_handling",
    # Mostly for owner/mods
    "mrfreeze.cogs.maintenance",
    "mrfreeze.cogs.moderation",
    "mrfreeze.cogs.banish.banish",
    "mrfreeze.cogs.messages",

    # Functions directed towards regular users.
    "mrfreeze.cogs.user_cmds",
    "mrfreeze.cogs.about",
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

except FileNotFoundError:
    print(f"\n{colors.RED}Error: Bot token missing!{colors.RESET}\n" +
          "Please put your bot's token in a separate text file " +
          "called \"token\".\nThis file should be located in the " +
          "same directory as the bot files.")

except discord.errors.LoginFailure as e:
    print(f"\n{colors.RED}Error: Login failure{colors.RESET}")
    print(e)

except Exception as e:
    print(f"\n{colors.RED}Error: {e}{colors.RESET}")

    if str(e) == "Event loop stopped before Future completed.":
        print("This is normal if you've been mashing ^C to")
        print("shut it down, otherwise it's not normal.")
    sys.exit(0)
