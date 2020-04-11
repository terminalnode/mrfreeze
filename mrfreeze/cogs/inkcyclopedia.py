import csv
import logging
import os
import re
from typing import List, NamedTuple, Optional, Pattern, Set

from airtable.airtable import Airtable

import discord
from discord import Message
from discord.ext.commands.context import Context

from mrfreeze import checks
from mrfreeze.bot import MrFreeze
from mrfreeze.colors import CYAN, MAGENTA_B, RESET

from .cogbase import CogBase


# Small cog listening to all incoming messages looking for mentions of inks.
# Based on The Inkcyclopedia by klundtasaur:
# https://www.reddit.com/r/fountainpens/comments/5egjsa/klundtasaurs_inkcyclopedia_for_rfountainpens/
def setup(bot: MrFreeze) -> None:
    """Add the cog to the bot."""
    bot.add_cog(Inkcyclopedia(bot))


class InkyTuple(NamedTuple):
    """A NamedTuple-class used to store information pertaining to an ink entry."""

    name:  str
    url:   str
    regex: Pattern[str]


class Inkcyclopedia(CogBase):
    """Type an ink inside {curly brackets} and I'll tell you what it looks like."""

    def __init__(self, bot: MrFreeze) -> None:
        self.bot: MrFreeze = bot

        self.inkydb:     Set[InkyTuple] = set()
        self.inkdb_path: str = f"{bot.db_prefix}/inkcyclopedia.csv"
        self.inkdb_enc:  str = "utf-8-sig"
        self.airtable:   Optional[Airtable] = None
        self.bracketmatch = re.compile(r"[{]([\w\-\s]+)[}]")
        self.logger = logging.getLogger(self.__class__.__name__)

        # File config/airtable should have format:
        # base = <your base id here>
        # table = <your table name here>
        # apikey = <your api_key here>
        try:
            with open("config/airtable", "r") as airtable_file:
                content = [i.split("=") for i in airtable_file.readlines()]
                content = [[i[0].strip(), i[1].strip()] for i in content]
                keys = {i[0]: i[1] for i in content}
                self.airtable = Airtable(
                    keys["base"],
                    keys["table"],
                    api_key = keys["apikey"]
                )
        except Exception:
            logmsg = "Failed to open or parse ./config/airtable."
            logmsg += "The Inkcyclopedia will not be able to update."
            self.logger.error(logmsg)

    @CogBase.listener()
    async def on_ready(self) -> None:
        """
        Prepare the Inkcyclopedia when the bot is ready.

        Fetch inks if database does not exist.
        Update db (loading the inks into memory).
        Then print status.
        """
        if not os.path.isfile(self.inkdb_path):
            await self.fetch_inks()

        await self.update_db()

        # Print that the ink database has been loaded and with how many inks.
        status =  f"{CYAN}The ink database has been loaded with "
        status += f"{MAGENTA_B}{len(self.inkydb)} inks{CYAN}!{RESET}"
        self.logger.info(status)

    async def fetch_inks(self) -> None:
        """Fetch the latest version of the Inkcyclopedia from Airtable."""
        with open(self.inkdb_path, "w", encoding=self.inkdb_enc) as inkfile:
            # Abort if self.airtable is not set.
            if self.airtable is not None:
                fetch = self.airtable.get_all()
            else:
                return

            writer = csv.writer(inkfile)
            for row in fetch:
                try:
                    fields = row["fields"]
                    inkname = fields["Ink Name"]
                    to_file: List[str] = [
                        fields["Ink Name"],
                        fields["RegEx"],
                        fields["Inkbot version"]
                    ]
                    if "N38sjv2.jpg" not in to_file[2]:
                        writer.writerow(to_file)
                except Exception:
                    # One of the fields is missing, we can't use this row
                    self.logger.warn(f"Failed to add {inkname}")
                    pass

    async def update_db(self) -> None:
        """
        Load all the inks into memory.

        Read the ink file from disk and create the ink database.
        """
        with open(self.inkdb_path, encoding=self.inkdb_enc) as inkfile:
            reader = csv.reader(inkfile)
            self.inkydb = set()

            for row in reader:
                ink = row[0]
                regex = row[1]
                url = row[2]
                self.inkydb.add(
                    InkyTuple(ink, url, re.compile(regex, re.IGNORECASE))
                )

    @discord.ext.commands.command(name="inkupdate")
    @discord.ext.commands.check(checks.is_owner)
    async def inkupdate(self, ctx: Context) -> None:
        """
        Let the bot owner force the bot to reload the inks into memory.

        Airtable is terribly annoying about fetching tables. Basically you
        can't just get it from the real table because you don't have a valid
        API key for that table or something, even if it's publicly available.
        So instead you have to manually copy it over to a table you own and
        fetch that table.

        Hence it's kind of pointless to do periodic checks and much better
        to simply force fetch it when you know there are updates available.
        """
        await self.fetch_inks()
        await self.update_db()
        await ctx.send(
            f"There are now {len(self.inkydb)} inks in the database!")
        self.log_command(
            ctx, f"Inkcyclopedia updated, now has {len(self.inkydb)} entries.")

    @CogBase.listener()
    async def on_message(self, message: Message) -> None:
        """Read every message, detect requests for ink pictures."""
        matches: List[str] = self.bracketmatch.findall(message.content)
        # Stop the function if message was sent by a bot or contains no matches
        if message.author.bot or not matches:
            return

        for match in matches:
            for ink in self.inkydb:
                if ink.regex.findall(match):
                    image = discord.Embed()
                    image.set_image(url=ink.url)
                    await message.channel.send(
                        f"Found a match for {ink.name}!",
                        embed=image)
                    # Only return the first hit, then return.
                    return
