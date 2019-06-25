import discord  # Basic discord functionality

def setup(bot):
    bot.add_cog(PinHandlerCog(bot))

class PinHandlerCog(discord.ext.commands.Cog, name='PinHandler'):
    """Posts the content of a message that was just pinned to chat."""
    def __init__(self, bot):
        self.bot = bot
        self.pinsDict = None

    @discord.ext.commands.Cog.listener()
    async def on_ready(self):
        pinsDict = dict()
        for guild in self.bot.guilds:
            pinsDict[guild.id] = dict()
            for channel in guild.channels:
                if isinstance(channel, discord.channel.TextChannel):
                    try:
                        pinsDict[guild.id][channel.id] = len(await channel.pins())
                        print( f"{self.bot.CYAN}Fetched pins from {self.bot.RED_B}{guild.name} {self.bot.GREEN_B}{channel.name}{self.bot.RESET}" )

                        if channel.id == 466241532458958850 and len(self.bot.guilds) == 2:
                            # This is for debugging purposes because the dict takes forever to build.
                            self.pinsDict = pinsDict
                            print (f"{self.bot.CYAN_B}PinsDict all done!{self.bot.RESET}")
                            return
                    except: pass # Channel probably got deleted.

        self.pinsDict = pinsDict
        print (f"{self.bot.CYAN_B}PinsDict all done!{self.bot.RESET}")

    @discord.ext.commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel, last_pin):
        # Unfortunately we have to cast an empty return
        # if the dict isn't finished yet.
        if self.pinsDict == None:
            print (f"{self.bot.CYAN}The {self.bot.RED_B}pinsDict{self.bot.CYAN} isn't finished yet!{self.bot.RESET}")
            return

        # The channel might be new, if so we need to create an entry for it.
        try:                self.pinsDict[channel.guild.id][channel.id]
        except KeyError:    self.pinsDict[channel.guild.id][channel.id] = 0

        # For comparisson between the two. These numbers will be
        # used to determine whether a pin was added or removed.
        channel_pins = await channel.pins()
        old_pins = self.pinsDict[channel.guild.id][channel.id]
        new_pins = len(channel_pins)

        # Was a new pin added?

        # If a pin was added when the bot was starting up, this won't work.
        # But it will work the next time as the pinsDict is updated.
        if new_pins > old_pins: was_added = True
        else:                   was_added = False

        # Updating the list of pins.
        self.pinsDict[channel.guild.id][channel.id] = new_pins

        if was_added:
            message = channel_pins[0]
            pinned_message = discord.Embed(description = message.content, color=0x00dee9)
            pinned_message.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)

            # Attaching first attachment of the post, if there are any.
            if message.attachments: pinned_message.set_image(url=message.attachments[0].url)

            channel_history = message.channel.history(limit=10)
            for i in range(10):
                sys_msg = await channel_history.next()
                if isinstance(sys_msg.type, type(discord.MessageType.pins_add)):
                    author = sys_msg.author.mention # This is the person who pinned the message.
                    await sys_msg.delete()
                    break # No need to look further.

            await channel.send(f"The following message was just pinned by {author}:\n", embed=pinned_message)
