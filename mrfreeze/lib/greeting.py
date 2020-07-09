"""Module for printing the bot greeting message."""
from mrfreeze.lib import colors


def bot_greeting(bot):
    """Print an attractive greeting message with some bot stats."""
    # Attractive greeting message with a couple of stats.
    number_of_channels = sum([len(guild.text_channels)
                              for guild in bot.guilds])
    greeting = [
        f"{colors.CYAN}{colors.CYAN_B} We have logged in as {bot.user}",
        f"{colors.CYAN}User name:           {colors.CYAN_B}{bot.user.name}",
        f"{colors.CYAN}User ID:             {colors.CYAN_B}{bot.user.id}",
        f"{colors.CYAN}Number of servers:   {colors.CYAN_B}{len(bot.guilds)}",
        f"{colors.CYAN}Number of channels:  {colors.CYAN_B}{number_of_channels}",
        f"{colors.CYAN}Number of users:     {colors.CYAN_B}{len(bot.users)}",
    ]

    # Calculating box width...
    # - Each escape character takes up 8 spaces.
    # - We then need two extra characters on each side.
    longest = max(greeting, key=lambda x: len(x) - 16)
    linewidth = (len(longest) - 16)
    box = f"{colors.CYAN}#{colors.RESET}"
    edges = f"{colors.CYAN}{'#' * (linewidth + 4)}{colors.RESET}"

    result = [ edges ]
    for line in greeting:
        width = (len(line) - 16)
        line += (" " * (linewidth - width))
        result.append(f"{box} {line} {box}")
    result.append(edges)
    return result
