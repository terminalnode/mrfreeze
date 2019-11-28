def create_colors(bot):
    # Colors codes to easily colorise output throughout the bot.
    bot.BLACK, bot.BLACK_B = "\033[00;30m", "\033[30;01m"
    bot.RED, bot.RED_B = "\033[00;31m", "\033[31;01m"
    bot.GREEN, bot.GREEN_B = "\033[00;32m", "\033[32;01m"
    bot.YELLOW, bot.YELLOW_B = "\033[00;33m", "\033[33;01m"
    bot.BLUE, bot.BLUE_B = "\033[00;34m", "\033[34;01m"
    bot.MAGENTA, bot.MAGENTA_B = "\033[00;35m", "\033[35;01m"
    bot.CYAN, bot.CYAN_B = "\033[00;36m", "\033[36;01m"
    bot.WHITE, bot.WHITE_B = "\033[00;37m", "\033[37;01m"
    bot.RESET = "\033[00000m"


def color_test(bot):
    print(f"{bot.CYAN_B}Color test: " +
          f"{bot.BLACK}#" +
          f"{bot.BLACK_B}#" +
          f"{bot.RED}#" +
          f"{bot.RED_B}#" +
          f"{bot.GREEN}#" +
          f"{bot.GREEN_B}#" +
          f"{bot.YELLOW}#" +
          f"{bot.YELLOW_B}#" +
          f"{bot.BLUE}#" +
          f"{bot.BLUE_B}#" +
          f"{bot.MAGENTA}#" +
          f"{bot.MAGENTA_B}#" +
          f"{bot.CYAN}#" +
          f"{bot.CYAN_B}#" +
          f"{bot.WHITE}#" +
          f"{bot.WHITE_B}#" +
          f"{bot.RESET} " +
          " RESET")
