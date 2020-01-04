"""Module for printing the bot greeting message."""
from mrfreeze import colors


def bot_greeting(bot):
    """Print an attractive greeting message with some bot stats."""
    # Attractive greeting message with a couple of stats.
    number_of_channels = sum([len(guild.text_channels)
                              for guild in bot.guilds])
    greeting = list()
    greeting.append(f"{colors.CYAN}{colors.CYAN_B}" +
                    f"We have logged in as {bot.user}")
    greeting.append(f"{colors.CYAN}User name:           " +
                    f"{colors.CYAN_B}{bot.user.name}")
    greeting.append(f"{colors.CYAN}User ID:             " +
                    f"{colors.CYAN_B}{bot.user.id}")
    greeting.append(f"{colors.CYAN}Number of servers:   " +
                    f"{colors.CYAN_B}{len(bot.guilds)}")
    greeting.append(f"{colors.CYAN}Number of channels:  " +
                    f"{colors.CYAN_B}{number_of_channels}")
    greeting.append(f"{colors.CYAN}Number of users:     " +
                    f"{colors.CYAN_B}{len(bot.users)}")

    # Calculating box width...
    # - Each escape character takes up 8 spaces.
    # - We then need two extra characters on each side.
    longest = max(greeting, key=lambda x: len(x) - 16)
    linewidth = (len(longest) - 16)
    box = f"{colors.CYAN}#{colors.RESET}"
    edges = f"{colors.CYAN}{'#' * (linewidth + 4)}{colors.RESET}"

    print(edges)
    for line in greeting:
        width = (len(line) - 16)
        line += (" " * (linewidth - width))
        print(f"{box} {line} {box}")
    print(edges)
