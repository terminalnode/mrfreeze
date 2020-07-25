"""Cog for logging when users join or leave a server."""
from typing import List

import discord
from discord import Embed
from discord import Member
from discord import TextChannel
from discord.ext.commands import Cog

from mrfreeze.bot import MrFreeze


def setup(bot: MrFreeze) -> None:
    """Add the cog to the bot."""
    bot.add_cog(DeparturesAndArrivals(bot))


class DeparturesAndArrivals(Cog):
    """Manages how the bot acts when a member leaves a server."""

    def __init__(self, bot: MrFreeze) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        """Log when a member leaves the chat."""
        if self.bot.listener_block_check(member):
            return

        guild_channels: List[TextChannel] = member.guild.text_channels
        mod_channel: TextChannel = discord.utils.get(guild_channels, name="leaving-messages")
        mention: str = member.mention
        username: str = f"{member.name}#{member.discriminator}"

        embed = Embed(color=0x00dee9)
        embed.set_thumbnail(url=member.avatar_url_as(static_format="png"))

        embed_text = f"{mention} is a smudgerous trech who's turned their back on "
        embed_text += f"{member.guild.name}.\n\n"
        embed_text += f"We're now down to {len(member.guild.members)} members."
        embed.add_field(name=f"{username} has left the server! :sob:", value=embed_text)
        await mod_channel.send(embed=embed)

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        """Log when a member joins the chat."""
        if self.bot.listener_block_check(member):
            return

        guild = member.guild.name
        # Penposium rules channel
        rules_channel = discord.utils.get(member.guild.channels, name="rules")

        msg = f"Welcome to {guild}, {member.mention}!\n"
        msg += "Please specify your region using `!region <region name>` to get a snazzy color "
        msg += "for your nickname.\nThe available regions are: Asia, Europe, North America, "
        msg += "South America, Africa, Oceania, Middle East and Antarctica."

        if rules_channel:
            msg += f"\n\nDon't forget to read the {rules_channel.mention}!"

        await member.guild.system_channel.send(msg)
