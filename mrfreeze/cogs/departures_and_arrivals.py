from typing import List

import discord
from discord import Embed, Member, TextChannel

from mrfreeze.bot import MrFreeze
from mrfreeze.cogs.cogbase import CogBase


def setup(bot):
    """Add the cog to the bot."""
    bot.add_cog(DeparturesAndArrivals(bot))


class DeparturesAndArrivals(CogBase):
    """Manages how the bot acts when a member leaves a server."""
    def __init__(self, bot: MrFreeze):
        self.bot = bot

    @CogBase.listener()
    async def on_member_remove(self, member: Member):
        guild_channels: List[TextChannel] = member.guild.text_channels
        mod_channel: TextChannel = discord.utils.get(guild_channels, name="mod-discussion")
        mention: str = member.mention
        username: str = f"{member.name}#{member.discriminator}"

        embed = Embed(color=0x00dee9)
        embed.set_thumbnail(url=member.avatar_url_as(static_format="png"))
        embed.add_field(
            name=f"{username} has left the server! :sob:",
            value=(
                f"{mention} is a smudgerous trech " +
                f"who's turned their back on {member.guild.name}.\n\n" +
                f"We're now down to {len(member.guild.members)} members."
            )
        )
        await mod_channel.send(embed=embed)

    @CogBase.listener()
    async def on_member_join(self, member: Member):
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
