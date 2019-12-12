import discord
from discord import TextChannel

from mrfreeze import colors
from mrfreeze.cogs.cogbase import CogBase


def setup(bot):
    """Add the cog to the bot."""
    bot.add_cog(PinHandler(bot))


class PinHandler(CogBase):
    """Post the content of a message that was just pinned to chat."""

    def __init__(self, bot):
        """Initialize the PinHandler cog."""
        self.bot = bot
        self.pinsDict = None

    @CogBase.listener()
    async def on_ready(self):
        pinsDict = dict()
        guilds = self.bot.guilds

        for guild in guilds:
            pinsDict[guild.id] = dict()
            for channel in guild.channels:
                if isinstance(channel, TextChannel):
                    try:
                        pinsDict[guild.id][channel.id] = len(await channel.pins())
                        print( f"{colors.CYAN}Fetched pins from {colors.RED_B}{guild.name} {colors.GREEN_B}{channel.name}{colors.RESET}" )

                        if channel.id == 466241532458958850 and len(guilds) == 2:
                            # This is for debugging purposes because the dict takes forever to build.
                            self.pinsDict = pinsDict
                            print (f"{colors.CYAN_B}PinsDict all done!{colors.RESET}")
                            return
                    except Exception:
                        pass  # Channel probably got deleted or something.

        self.pinsDict = pinsDict
        print (f"{colors.CYAN_B}PinsDict all done!{colors.RESET}")

    @CogBase.listener()
    async def on_guild_channel_pins_update(self, channel, last_pin):
        # Unfortunately we have to cast an empty return
        # if the dict isn't finished yet.
        if self.pinsDict is None:
            print(f"{colors.CYAN}The {colors.RED_B}pinsDict " +
                  f"{colors.CYAN}isn't finished yet!{colors.RESET}")
            return

        # The channel might be new, if so we need to create an entry for it.
        try:
            self.pinsDict[channel.guild.id][channel.id]
        except KeyError:
            self.pinsDict[channel.guild.id][channel.id] = 0

        # For comparisson between the two. These numbers will be
        # used to determine whether a pin was added or removed.
        channel_pins = await channel.pins()
        old_pins = self.pinsDict[channel.guild.id][channel.id]
        new_pins = len(channel_pins)

        # Was a new pin added?

        # If a pin was added when the bot was starting up, this won't work.
        # But it will work the next time as the pinsDict is updated.
        was_added = False
        if new_pins > old_pins:
            was_added = True

        # Updating the list of pins.
        self.pinsDict[channel.guild.id][channel.id] = new_pins

        if was_added:
            message = channel_pins[0]
            pinned_message = discord.Embed(
                description=message.content,
                color=0x00dee9)
            pinned_message.set_author(
                name=message.author.display_name,
                icon_url=message.author.avatar_url)

            # Attaching first attachment of the post, if there are any.
            if message.attachments:
                pinned_message.set_image(url=message.attachments[0].url)

            channel_history = message.channel.history(limit=10)
            for _ in range(10):
                sysmsg = await next(channel_history)
                if isinstance(sysmsg.type, type(discord.MessageType.pins_add)):
                    # This is the person who pinned the message.
                    author = sysmsg.author.mention
                    await sysmsg.delete()
                    # No need to look further.
                    break

            await channel.send(
                    f"The following message was just pinned by {author}:\n",
                    embed=pinned_message)
