"""Module that keeps tabs on what posts are pinned and whenever there's a change to them."""

import functools
import logging
import operator
from datetime import datetime
from typing import Dict, Iterable, List, Optional

import discord
from discord import Message, MessageType, TextChannel
from discord.abc import GuildChannel
from discord.ext.commands.bot import Bot

from mrfreeze import colors
from mrfreeze.cogs.cogbase import CogBase


def setup(bot: Bot) -> None:
    """Add the cog to the bot."""
    bot.add_cog(PinHandler(bot))


class PinHandler(CogBase):
    """Post the content of a message that was just pinned to chat."""

    def __init__(self, bot: Bot) -> None:
        """Initialize the PinHandler cog."""
        self.bot = bot
        self.pinsDict: Optional[Dict[int, int]] = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("PinHandler initialized")

    @CogBase.listener()
    async def on_ready(self) -> None:
        """When ready, make a list of the number of pins in all channels."""
        # Type declarations
        all_channel_lists: Iterable[List[GuildChannel]]
        all_channels: Iterable[GuildChannel]
        text_channels: Iterable[TextChannel]
        pinsDict: Dict[int, int]

        guilds = self.bot.guilds
        pinsDict = dict()

        # Create iterable of all text channes
        all_channel_lists = map(lambda g: g.channels, guilds)
        all_channels = functools.reduce(operator.iconcat, all_channel_lists, [])
        text_channels = filter(lambda c: isinstance(c, TextChannel), all_channels)

        for channel in text_channels:
            guild = channel.guild.name

            try:
                num_pins = len(await channel.pins())
                pinsDict[channel.id] = num_pins

                log = f"{colors.CYAN}{num_pins} pins in {colors.RED_B}{guild} "
                log += f"{colors.GREEN_B}#{channel.name}{colors.RESET}"
                self.logger.info(log)

                if channel.id == 466241532458958850 and len(guilds) == 2:
                    # This is for debugging purposes because the dict takes forever to build.
                    self.pinsDict = pinsDict
                    self.logger.info(f"{colors.CYAN_B}PinsDict all done!{colors.RESET}")
                    return

            except Exception as e:
                log = f"Encountered {e} fetching pins from {colors.RED_B}{guild.name} "
                log += f"{colors.GREEN_B}{channel.name}{colors.RESET}"
                self.logger.error(log)
                pass  # Channel probably got deleted or something.

        self.pinsDict = pinsDict
        self.logger.info(f"{colors.CYAN_B}PinsDict all done!{colors.RESET}")

    @CogBase.listener()
    async def on_guild_channel_pins_update(
            self,
            channel: TextChannel,
            last_pin: Optional[datetime]) -> None:
        """
        Post a message when a new pin is added to a channel.

        The pin system is kind of stupid, it doesn't tell us whether a pin was
        added or removed from the channel, just that there was a change. So we
        have an index of how many pins each channel had before and use that to
        determine whether a pin was added or deleted.

        Because discord is being ridiculous and having is keep track of this
        ourselves, it's very easy to get rate limited doing this. When that
        happens however, usually the bot will automatically retry again within
        five seconds and fix it.
        """
        # If the pinsDict isn't done yet, log an error and return.
        if self.pinsDict is None:
            msg = f"{colors.CYAN}The {colors.RED_B}pinsDict "
            msg += f"{colors.CYAN}isn't finished yet!{colors.RESET}"
            self.logger.warn(msg)
            return

        # The channel might be new, if so we need to create an entry for it.
        if channel.id not in self.pinsDict:
            self.pinsDict[channel.id] = 0

        # For comparisson between the two. These numbers will be
        # used to determine whether a pin was added or removed.
        channel_pins: List[Message] = await channel.pins()
        new_pins = len(channel_pins)
        old_pins = self.pinsDict[channel.id]
        was_added = new_pins > old_pins

        # Updating the list of pins.
        self.pinsDict[channel.id] = new_pins

        if was_added:
            message = channel_pins[0]
            author_name = message.author.display_name
            author_pic = message.author.avatar_url
            content = message.content

            pinned_message = discord.Embed(description=content, color=0x00dee9)
            pinned_message.set_author(name=author_name, icon_url=author_pic)

            # Attaching first attachment of the post, if there are any.
            if message.attachments:
                pinned_message.set_image(url=message.attachments[0].url)

            history = channel.history(limit=10)
            sysmsg = await history.find(
                lambda m: isinstance(m.type, type(MessageType.pins_add)))

            if sysmsg is not None:
                pinner = sysmsg.author.mention
                await sysmsg.delete()
            else:
                pinner = "Some mod"

            msg = f"The following message was just pinned by {pinner}:\n"
            await channel.send(msg, embed=pinned_message)
