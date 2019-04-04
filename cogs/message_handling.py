import discord, re
from discord.ext import commands
from botfunctions import temp

class MessageHandlerCog(commands.Cog, name='MessageHandler'):
    """How the bot acts when messages are posted."""
    def __init__(self, bot):
        self.bot = bot

    # Certain events, namely temp, depends on checking for
    # temperature statements in all messages sent to the chat.

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        # the trailing space let's us match temperatures at the end of the message.
        tempstatement = re.search('(( -)?\d+[,.]?(\d+)?) ?(?:°?d(eg)?(egrees)?|°?c(elcius)?(elsius)?(ivilized( units)?)?(ivilised( units)?)?(u)?|' +
                                  '°?f(ahrenheit)?(reedom( units)?)?(u)?|°?k(elvin)?|°?r(ankine)?)[^\w]',
                                  ' ' + message.content.lower() + ' ')

        if message.author == self.bot.user:
            pass # Ignore what the bot says...

        elif tempstatement != None:
            await temp.convert(ctx, tempstatement)

        elif (self.bot.user in message.mentions):
            await ctx.send(message.author.mention + ' wtf do you want smud?')

def setup(bot):
    bot.add_cog(MessageHandlerCog(bot))
