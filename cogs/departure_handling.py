import discord
from discord.ext import commands

class DepartureHandlerCog(commands.Cog, name='DepartureHandler'):
    """How the bot acts when members leave the chat."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        mod_channel = discord.utils.get(member.guild.channels, name='mod-discussion')
        member_name = str(member.name + '#' + str(member.discriminator))
        member_count = str(len(member.guild.members))

        embed = discord.Embed(color=0x00dee9)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field( name='A member has left the server! :sob:',
                         value=('**%s#%s** is a smudgerous trech who\'s turned their back on %s. We now have only %s members.' %
                         (member.name, str(member.discriminator), member.guild.name, member_count)) )
        await mod_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(DepartureHandlerCog(bot))
