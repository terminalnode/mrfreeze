import discord
import datetime

class CogBase(discord.ext.commands.Cog):
    def initialize_colors(self):
        """Initialize colors for self, useful for logging and stuff."""
        self.BLACK,   self.BLACK_B    = '\033[00;30m', '\033[30;01m'
        self.RED,     self.RED_B      = '\033[00;31m', '\033[31;01m'
        self.GREEN,   self.GREEN_B    = '\033[00;32m', '\033[32;01m'
        self.YELLOW,  self.YELLOW_B   = '\033[00;33m', '\033[33;01m'
        self.BLUE,    self.BLUE_B     = '\033[00;34m', '\033[34;01m'
        self.MAGENTA, self.MAGENTA_B  = '\033[00;35m', '\033[35;01m'
        self.CYAN,    self.CYAN_B     = '\033[00;36m', '\033[36;01m'
        self.WHITE,   self.WHITE_B    = '\033[00;37m', '\033[37;01m'
        self.RESET                    = '\033[00000m'

    def current_time(self):
        """Good time stamps for consistent console messages throughout the bot."""
        current_time = datetime.datetime.now()
        formated_time = datetime.datetime.strftime(current_time, '%Y-%m-%d %H:%M')
        return f"{self.CYAN_B}{formated_time}{self.RESET}"

    def mentions_list(self, mentions):
        """Create a string of mentions from a list of user objects."""
        mentions = [ user.mention for user in mentions ]
        if len(mentions) == 0:      return "No one"
        elif len(mentions) == 1:    return mentions[0]
        else:                       return ", ".join(mentions[:-1]) + f" and {mentions[-1]}"

    def get_mute_role(self, guild):
        """Currently just gives the role with the name antarctica.
        In the future this may be expanded so servers can designate whatever role they want as Antarctica."""
        for role in guild.roles:
            if role.name.lower() == "antarctica":
                return role
        return None
