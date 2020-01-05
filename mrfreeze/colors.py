import re

BLACK = "\033[00;30m"
BLACK_B = "\033[30;01m"
RED = "\033[00;31m"
RED_B = "\033[31;01m"
GREEN = "\033[00;32m"
GREEN_B = "\033[32;01m"
YELLOW = "\033[00;33m"
YELLOW_B = "\033[33;01m"
BLUE = "\033[00;34m"
BLUE_B = "\033[34;01m"
MAGENTA = "\033[00;35m"
MAGENTA_B = "\033[35;01m"
CYAN = "\033[00;36m"
CYAN_B = "\033[36;01m"
WHITE = "\033[00;37m"
WHITE_B = "\033[37;01m"
RESET = "\033[00000m"
regexp = re.compile(r'(\033\[\d+;?\d*m)')


def strip(string: str):
    """Strip a string of all escape sequences."""
    return regexp.sub("", string)


def color_test():
    """Print all the colors for visual inspection."""
    print(f"{CYAN_B}Color test: " +
          f"{BLACK}#" +
          f"{BLACK_B}#" +
          f"{RED}#" +
          f"{RED_B}#" +
          f"{GREEN}#" +
          f"{GREEN_B}#" +
          f"{YELLOW}#" +
          f"{YELLOW_B}#" +
          f"{BLUE}#" +
          f"{BLUE_B}#" +
          f"{MAGENTA}#" +
          f"{MAGENTA_B}#" +
          f"{CYAN}#" +
          f"{CYAN_B}#" +
          f"{WHITE}#" +
          f"{WHITE_B}#" +
          f"{RESET} " +
          " RESET")
