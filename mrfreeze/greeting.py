def bot_greeting(bot):
    # Attractive greeting message with a couple of stats.
    greeting = list()
    greeting.append(f'{bot.CYAN}{bot.CYAN_B}We have logged in as {bot.user}')
    greeting.append(f'{bot.CYAN}User name:           {bot.CYAN_B}{bot.user.name}')
    greeting.append(f'{bot.CYAN}User ID:             {bot.CYAN_B}{bot.user.id}')
    greeting.append(f'{bot.CYAN}Number of servers:   {bot.CYAN_B}{len(bot.guilds)}')
    greeting.append(f'{bot.CYAN}Number of channels:  {bot.CYAN_B}{sum([ len(guild.text_channels) for guild in bot.guilds ])}')
    greeting.append(f'{bot.CYAN}Number of users:     {bot.CYAN_B}{len(bot.users)}')
    
    # Calculating box width...
    # - Each escape character takes up 8 spaces.
    # - We then need two extra characters on each side.
    longest = max(greeting, key=lambda x: len(x)-16)
    linewidth = (len(longest) - 16)
    box = f"{bot.CYAN}#{bot.RESET}"
    
    print(f"{ box * (linewidth + 4) }")
    for line in greeting:
        width = ( len(line) - 16 )
        line += ( ' ' * (linewidth - width) )
        print(f"{box} {line} {box}")
    print(f"{ box * (linewidth + 4) }")
