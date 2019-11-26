import discord
from discord import Embed
from internals.cogbase import CogBase

# Some imports used in type hints
from discord import Member, TextChannel
from internals.mrfreeze import MrFreeze
from typing import List


def setup(bot):
    bot.add_cog(Departures(bot))


class Departures(CogBase):
    """
    How the bot acts when members leave the chat.
    """
    def __init__(self, bot: MrFreeze):
        self.bot = bot

    @CogBase.listener()
    async def on_member_remove(self, member: Member):
        guild_channels: List[TextChannel] = member.guild.text_channels
        mod_channel: TextChannel = discord.utils.get(
                guild_channels,
                name="mod-discussion")
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
