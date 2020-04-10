"""Import all cogs, set log level and starts the bot."""

import logging
import sys
import traceback

import discord

from mrfreeze import bot
from mrfreeze.colors import BLUE_B, CYAN, CYAN_B, MAGENTA_B, RED, RESET

# Set general logging to warn, this will display warnings
# from various modules we have imported such as discord,
# then set the format for our logs
LOG_FORMAT  = f"{BLUE_B}%(levelname)s "
LOG_FORMAT += f"{CYAN_B}%(asctime)s "
LOG_FORMAT += f"{MAGENTA_B}%(name)s: "
LOG_FORMAT += f"{CYAN}%(message)s{RESET}"
logging.basicConfig(level  = logging.WARN,
                    format = LOG_FORMAT,
                    datefmt = "%Y-%m-%d %H:%M:%S")

# Set log levels for MrFreeze modules
logging.getLogger("mrfreeze").setLevel(logging.INFO)
logging.getLogger("CommandLogger").setLevel(logging.INFO)
logging.getLogger("Inkcyclopedia").setLevel(logging.INFO)
logging.getLogger("MrFreeze").setLevel(logging.INFO)

# Get logger for this module
logger = logging.getLogger("BotInit")
logger.setLevel(logging.WARN)

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
            logger.debug(f"Loading cog: {cog}")
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
    logger.debug(f"Token is: {token}")
    bot.run(token, bot=True, reconnect=True)

except FileNotFoundError:
    msg = f"\n{RED}Error: Bot token missing!{RESET}\n"
    msg += "Please put your bot's token in a separate text file "
    msg += "called \"token\".\nThis file should be located in the "
    msg += "same directory as the bot files."
    logger.error(msg)

except discord.errors.LoginFailure as e:
    logger.error(f"{RED}Error: Login failure{RESET}")
    print(e)

except Exception as e:
    msg = f"{RED}Error: {e}{RESET}"
    logger.error(msg)

    if str(e) == "Event loop stopped before Future completed.":
        its_ok = "This is normal if you've been mashing ^C to "
        its_ok += "shut it down, otherwise it's not normal."
        logger.error(its_ok)
    sys.exit(0)
