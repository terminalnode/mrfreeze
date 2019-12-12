"""Module for setting up the various paths which the bot requires."""
import os
import sys

from mrfreeze import colors


def path_setup(path, trivial_name):
    """Create various directories which the bot needs."""
    if os.path.isdir(path):
        print(f"{colors.GREEN_B}{trivial_name} {colors.GREEN}({path}) " +
              f"{colors.CYAN}exists and is a directory.{colors.RESET}")
    elif os.path.exists(path):
        print(f"{colors.RED_B}{trivial_name} {colors.RED}({path}) " +
              f"{colors.CYAN}exists but is not a directory. " +
              f"Aborting.{colors.RESET}")
        sys.exit(0)
    else:
        try:
            os.makedirs(path)
            print(f"{colors.GREEN_B}{trivial_name} {colors.GREEN}({path}) " +
                  f"{colors.CYAN}was successfully created.{colors.RESET}")
        except Exception as e:
            print(f"{colors.RED_B}{trivial_name} {colors.RED}({path}) " +
                  f"{colors.CYAN} does not exist and could not be created:\n" +
                  f"{colors.RED}==> {e}{colors.RESET}")
            sys.exit(0)
