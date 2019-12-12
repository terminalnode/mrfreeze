"""A base from which all other cogs inherit."""
import datetime
from typing import List
from typing import Optional

from discord import Guild
from discord import Role
from discord import User
from discord.ext.commands import Cog
from discord.ext.commands.context import Context

from mrfreeze import colors


class CogBase(Cog):
    """
    Base cog from which all other cogs inherit.

    Contains functions common for all cogs.
    """

    def current_time(self) -> str:
        """Good time stamps for consistent consoprintts throughout the bot."""
        current_time = datetime.datetime.now()
        formated_time = datetime.datetime.strftime(
            current_time,
            "%Y-%m-%d %H:%M")
        return f"{colors.CYAN_B}{formated_time}{colors.RESET}"

    def mentions_list(self, mentions: List[User]) -> str:
        """Create a string of mentions from a list of user objects."""
        mentions = [user.mention for user in mentions]
        if len(mentions) == 0:
            return "No one"
        elif len(mentions) == 1:
            return mentions[0]
        else:
            return ", ".join(mentions[:-1]) + f" and {mentions[-1]}"

    def get_mute_role(self, guild: Guild) -> Optional[Role]:
        """
        Retrieve the designated mute role for the server.

        Currently just gives the role with the name antarctica.
        In the future this may be expanded so servers can designate
        whatever role they want as Antarctica.
        """
        for role in guild.roles:
            if role.name.lower() == "antarctica":
                return role
        return None

    def log_command(self, ctx: Context, text: str = "") -> None:
        """Print a message to the log whenever a command is executed."""
        # temporary, this will be removed once all cogs have transitioned
        print("Printed by selflogger:")

        time = f"{colors.CYAN_B}{self.current_time()}"

        command = f"{colors.CYAN_B}{ctx.prefix}{ctx.command}"

        author = (f"{colors.YELLOW}{ctx.author.name}#" +
                  f"{ctx.author.discriminator} {colors.CYAN}used")

        location = (f"{colors.CYAN}in {colors.GREEN}#" +
                    f"{ctx.channel}{colors.CYAN} @ " +
                    f"{colors.MAGENTA}{ctx.guild}")

        if not text:
            print(f"{time} {author} {command} {location}{colors.RESET}")
        else:
            text = f"{colors.CYAN}:\n{text}"
            print(f"{time} {author} {command} {location}{text}{colors.RESET}")

    def log_generic(self, text: str) -> None:
        """Print a more generic log message for other things than commands."""
        pass
