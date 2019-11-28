from discord.ext.commands import Cog
import datetime

# Used in type hints
from discord import Guild
from discord import Role
from discord import User
from discord.ext.commands.context import Context
from typing import List
from typing import Optional

class CogBase(Cog):
    def initialize_colors(self) -> None:
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

    def current_time(self) -> str:
        """
        Good time stamps for consistent console messages throughout the bot.
        """
        current_time = datetime.datetime.now()
        formated_time = datetime.datetime.strftime(current_time, '%Y-%m-%d %H:%M')
        return f"{self.CYAN_B}{formated_time}{self.RESET}"

    def mentions_list(self, mentions: List[User]) -> str:
        """
        Create a string of mentions from a list of user objects.
        """
        mentions = [ user.mention for user in mentions ]
        if len(mentions) == 0:      return "No one"
        elif len(mentions) == 1:    return mentions[0]
        else:                       return ", ".join(mentions[:-1]) + f" and {mentions[-1]}"

    def get_mute_role(self, guild: Guild) -> Optional[Role]:
        """
        Currently just gives the role with the name antarctica.
        In the future this may be expanded so servers can designate
        whatever role they want as Antarctica.
        """
        for role in guild.roles:
            if role.name.lower() == "antarctica":
                return role
        return None

    def log_command(self, ctx: Context, text: str = "") -> None:
        """
        Prints a message to the log whenever a command is executed.
        """

        print("Printed by selflogger:") # temporary, this will be removed once all cogs have transitioned
        time     = f"{self.CYAN_B}{self.current_time()}"
        author   = f"{self.YELLOW}{ctx.author.name}#{ctx.author.discriminator} {self.CYAN}used"
        command  = f"{self.CYAN_B}{ctx.prefix}{ctx.command}"
        location = f"{self.CYAN}in {self.GREEN}#{ctx.channel}{self.CYAN} @ {self.MAGENTA}{ctx.guild}"

        if not text:
            print(f"{time} {author} {command} {location}{self.RESET}")
        else:
            text = f"{self.CYAN}:\n{text}"
            print(f"{time} {author} {command} {location}{text}{self.RESET}")

    def log_generic(self, text: str) -> None:
        """
        Prints a more generic message to the log, used for other things than commands.
        """
        pass
