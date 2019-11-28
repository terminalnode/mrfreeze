import discord
# Airtable data is saved locally to file
import csv
# To ensure if the inkfile exists and if airtable settings exist
import os
# To check for inks in messages
import re
# The database is stored in an Airtable base
from airtable.airtable import Airtable
# To ensure only the bot owner can update the database
from mrfreeze import checks
# CogBase is a common base for all the cogs
from .cogbase import CogBase

# Some imports used in type hints
from discord import Message
from discord.ext.commands.context import Context
from mrfreeze.bot import MrFreeze
from typing import List, Optional, Pattern, Set, NamedTuple


# Small cog listening to all incoming messages looking for mentions of inks.
# Based on The Inkcyclopedia by klundtasaur:
# https://www.reddit.com/r/fountainpens/comments/5egjsa/klundtasaurs_inkcyclopedia_for_rfountainpens/
def setup(bot):
    bot.add_cog(Inkcyclopedia(bot))


class InkyTuple(NamedTuple):
    name:  str
    url:   str
    regex: Pattern[str]


class Inkcyclopedia(CogBase):
    """Type an ink inside {curly brackets} and I'll tell you what
    it looks like!"""
    def __init__(self, bot: MrFreeze) -> None:
        self.bot: MrFreeze = bot
        self.initialize_colors()

        self.inkydb:     Set[InkyTuple] = set()
        self.inkdb_path: str = "databases/dbfiles/inkcyclopedia.csv"
        self.inkdb_enc:  str = "utf-8-sig"
        self.airtable:   Optional[Airtable] = None
        self.bracketmatch = re.compile(r"[{]([\w\-\s]+)[}]")

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
                        api_key=keys["apikey"]
                )
        except Exception:
            print("Failed to open or parse ./config/airtable.")
            print("The Inkcyclopedia will not be able to update.")

    @CogBase.listener()
    async def on_ready(self) -> None:
        # Fetch inks if db does not exist
        if not os.path.isfile(self.inkdb_path):
            await self.fetch_inks()

        # Load up the ink db!
        await self.update_db()

        # Print that the ink database has been loaded and with how many inks.
        print(
            f"{self.CYAN}The ink database has been loaded with " +
            f"{self.MAGENTA_B}{len(self.inkydb)} inks{self.CYAN}!{self.RESET}"
        )

    async def fetch_inks(self) -> None:
        """Fetches the latest version of the Inkcyclopedia from Airtable."""
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
                    print(f"Failed to add {inkname}")
                    pass

    async def update_db(self) -> None:
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
        await self.fetch_inks()
        await self.update_db()
        await ctx.send(
            f"There are now {len(self.inkydb)} inks in the database!")
        self.log_command(
            ctx, f"Inkcyclopedia updated, now has {len(self.inkydb)} entries.")

    @CogBase.listener()
    async def on_message(self, message: Message) -> None:
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
