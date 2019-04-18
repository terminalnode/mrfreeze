import discord
from discord.ext import commands

class DepartureHandlerCog(commands.Cog, name='DepartureHandler'):
    """How the bot acts when members leave the chat."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        mod_channel = discord.utils.get(member.guild.channels, name='mod-discussion')

        embed = discord.Embed(color=0x00dee9)
        embed.set_thumbnail(url=member.avatar_url_as(static_format="png"))
        embed.add_field(
            name="A member has left the server! :sob:",
            value=(
                f"**{member.name}#{member.discriminator}** ({member.mention}) is a smudgerous trech " +
                f"who's turned their back on {member.guild.name}. " +
                f"We now have only {len(member.guild.members)} members."
            )
        )

        await mod_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(DepartureHandlerCog(bot))
