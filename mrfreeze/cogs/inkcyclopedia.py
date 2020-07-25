"""Cog for handling ink lookups via thisisverytricky's ink API."""
import logging
import re
from typing import List
from typing import Optional
from typing import Pattern
from typing import Set

import discord
from discord import Message
from discord.ext.commands import Cog
from discord.ext.commands import Context
from discord.ext.commands import command

from mrfreeze.bot import MrFreeze

import requests


def setup(bot: MrFreeze) -> None:
    """Add the cog to the bot."""
    bot.add_cog(Inkcyclopedia(bot))


class Ink:
    """A class used to store information pertaining to an ink entry."""

    id:         Optional[str]
    name:       Optional[str]
    url:        Optional[str]
    submitter:  Optional[str]
    alternates: List[str]
    review:     Optional[str]

    def __init__(self) -> None:
        self.id = None
        self.name = None
        self.url = None
        self.submitter = None
        self.alternates = list()
        self.review = None


class Inkcyclopedia(Cog):
    """Type an ink inside {curly brackets} and I'll tell you what it looks like."""

    def __init__(self, bot: MrFreeze) -> None:
        self.bot: MrFreeze = bot
        self.inkydb: Set[Ink] = set()
        self.url: str = "https://system-inks-api.us-e2.cloudhub.io/api/inks"
        self.bracketmatch: Pattern = re.compile(r"[{]([\w\-\s]+)[}]")

        self.logger = logging.getLogger(self.__class__.__name__)

    async def search_inks(self, inks: List[str]) -> List[Ink]:
        """Search for the listed inks in the Inkcyclopedia, return a list of inks."""
        try:
            response = requests.post(f"{self.url}/search", json=inks).json()["found"]
        except Exception:
            return []

        result: List[Ink] = list()
        for ink in response:
            body = response[ink]

            if "fullName" in body and "primaryImage" in body:
                ink = Ink()
                ink.id = body.get("id")
                ink.name = body.get("fullName")
                ink.url = body.get("primaryImage")
                ink.submitter = body.get("submittedBy")
                ink.review = body.get("reviewLink")

                alternates = body.get("alternateImages")
                if alternates:
                    ink.alternates = alternates

                if ink.name and ink.url:
                    result.append(ink)

        return result

    def get_mute_status(self, ctx: Context, is_muted: bool) -> str:
        """Check if inkcyclopedia is enabled for this server."""
        invocation = ctx.invoked_with

        if is_muted:
            msg = f"{ctx.author.mention} The {invocation} feature has been "
            msg += "**deactivated** for this server."
        else:
            msg = f"{ctx.author.mention} The {invocation} feature is "
            msg += "**active** for this server."

        return msg

    def get_changed_status(self, ctx: Context, before: bool, after: bool, want: bool) -> str:
        """Print a message saying if the inkcyclopedia has been activated or deactivated."""
        mention = ctx.author.mention
        invocation = ctx.invoked_with

        if before == want:
            if want:
                return f"{mention} The {invocation} is already deactivated."
            else:
                return f"{mention} The {invocation} is already active."

        elif after != want:
            msg = f"{mention} Something went wrong, I wasn't able to "
            if want:
                return msg + "deactivate the {invocation}."
            else:
                return msg + "activate the {invocation}."

        else:
            if after:
                return f"{mention} The {invocation} is now deactivated."
            else:
                return f"{mention} The {invocation} is now activated."

    @command(name="inkcyclopedia", aliases=[ "inkbot", "inkybot" ])
    async def inkcyclopedia_command(self, ctx: Context, *args: str) -> None:
        """Check or change inkcyclopedia mute status."""
        is_owner = await ctx.bot.is_owner(ctx.author)
        is_mod = ctx.author.guild_permissions.administrator
        is_muted = bool(self.bot.settings.is_inkcyclopedia_muted(ctx.guild))
        owner_or_mod = is_owner or is_mod
        msg: Optional[str] = None

        if len(args) == 0 or not owner_or_mod:
            msg = self.get_mute_status(ctx, is_muted)

        elif args[0].lower() == "on":
            if is_muted:
                self.bot.settings.toggle_inkcyclopedia_mute(ctx.guild)
                is_muted_after = bool(self.bot.settings.is_inkcyclopedia_muted(ctx.guild))
                msg = self.get_changed_status(ctx, is_muted, is_muted_after, False)
            else:
                msg = self.get_changed_status(ctx, is_muted, is_muted, False)

        elif args[0].lower() == "off":
            if is_muted:
                msg = self.get_changed_status(ctx, is_muted, is_muted, True)
            else:
                self.bot.settings.toggle_inkcyclopedia_mute(ctx.guild)
                is_muted_after = bool(self.bot.settings.is_inkcyclopedia_muted(ctx.guild))
                msg = self.get_changed_status(ctx, is_muted, is_muted_after, True)

        elif args[0].lower() == "toggle":
            self.bot.settings.toggle_inkcyclopedia_mute(ctx.guild)
            is_muted_after = bool(self.bot.settings.is_inkcyclopedia_muted(ctx.guild))
            msg = self.get_changed_status(ctx, is_muted, is_muted_after, not is_muted)

        else:
            msg = self.get_mute_status(ctx, is_muted)

        if msg:
            await ctx.send(msg)

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        """Read every message, detect requests for ink pictures."""
        if self.bot.listener_block_check(message):
            return
        elif message.guild and self.bot.settings.is_inkcyclopedia_muted(message.guild):
            return

        matches: List[str] = self.bracketmatch.findall(message.content)

        # Stop the function if message was sent by a bot or contains no matches
        if message.author.bot or not matches:
            return

        results: List[Ink] = await self.search_inks(matches)

        if results:
            ink = results[0]
            image = discord.Embed()
            image.title = ink.name
            image.set_image(url=ink.url)
            image.description = f"[Primary image link]({ink.url})"

            if ink.alternates:
                alternateUrls = [f"[[{index}]]({url})" for index, url in enumerate(ink.alternates)]
                alternativeImageLinks = " ".join(alternateUrls)
                image.add_field(name="Additional images", value=alternativeImageLinks)

            if ink.review:
                image.add_field(name="Review", value=ink.review)

            if ink.submitter:
                image.set_footer(text=f"Submitted by: {ink.submitter}")
            else:
                image.set_footer(text="Submitter unknown")

            await message.channel.send(embed=image)
