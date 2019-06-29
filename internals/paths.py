import os   # Required for interacting with the file system.
import sys  # Required for emergency exit when the required folder does not exist and can't be created.

def path_setup(bot, path, trivial_name):
    """This is part of the setup process. Creates various directories the bot needs."""
    if os.path.isdir(path):
        print(f"{bot.GREEN_B}{trivial_name} {bot.GREEN}({path}) {bot.CYAN}exists and is a directory.{bot.RESET}")
    elif os.path.exists(path):
        print(f"{bot.RED_B}{trivial_name} {bot.RED}({path}) {bot.CYAN}exists but is not a directory. Aborting.{bot.RESET}")
        sys.exit(0)
    else:
        try:
            os.makedirs(path)
            print(f"{bot.GREEN_B}{trivial_name} {bot.GREEN}({path}) {bot.CYAN}was successfully created.{bot.RESET}")
        except Exception as e:
            print(f"{bot.RED_B}{trivial_name} {bot.RED}({path}) {bot.CYAN} does not exist and could not be created:\n" +
                f"{bot.RED}==> {e}{bot.RESET}")
            sys.exit(0)
