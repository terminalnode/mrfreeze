import json
import logging
import re
from typing import List, NamedTuple, Optional, Pattern, Set

import discord
import requests
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


class Inkcyclopedia(CogBase):
    """Type an ink inside {curly brackets} and I'll tell you what it looks like."""

    def __init__(self, bot: MrFreeze) -> None:
        self.bot: MrFreeze = bot
        self.inkydb: Set[InkyTuple] = set()
        self.search_url: str = "https://system-inks-api.us-e2.cloudhub.io/api/inks/search"
        self.bracketmatch: Pattern = re.compile(r"[{]([\w\-\s]+)[}]")

        self.logger = logging.getLogger(self.__class__.__name__)

    async def search_inks(self, inks: List[str]) -> List[InkyTuple]:
        """Search for the listed inks in the Inkcyclopedia, return a list of inks."""
        try:
            response = requests.post(self.search_url, json=inks).json()["found"]
        except Exception:
            return []

        result: List[InkyTuple] = list()
        for ink in response:
            body = response[ink]

            if "fullName" in body and "primaryImage" in body:
                fullName: str = body["fullName"]
                url: str = body["primaryImage"]

                if fullName and url:
                    result.append(InkyTuple(fullName, url))

        return result

    @CogBase.listener()
    async def on_message(self, message: Message) -> None:
        """Read every message, detect requests for ink pictures."""
        if self.bot.listener_block_check(message):
            return

        matches: List[str] = self.bracketmatch.findall(message.content)

        # Stop the function if message was sent by a bot or contains no matches
        if message.author.bot or not matches:
            return

        results: List[InkyTuple] = await self.search_inks(matches)

        if results:
            ink = results[0]
            image = discord.Embed()
            image.set_author(name=ink.name)
            image.set_image(url=ink.url)
            await message.channel.send(embed=image)
