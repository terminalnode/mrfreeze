import discord, re
from discord.ext import commands

class MessageHandlerCog(commands.Cog, name='MessageHandler'):
    """How the bot acts when messages are posted."""
    def __init__(self, bot):
        self.bot = bot

    # Certain events, namely temp, depends on checking for
    # temperature statements in all messages sent to the chat.

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore what all the bots say...
        if message.author.bot: return

        ctx     = await self.bot.get_context(message)
        text    = message.content
        mention = message.author.mention
        roles   = message.author.roles
        await self.temperatures(text, ctx)

    async def temperatures(self, text, ctx):
        # Trailing space is required for matching temperatures at the end of the message.
        text = text.lower()
        author = ctx.author.mention
        roles = ctx.author.roles
        channel = ctx.channel

        # Extract temperature statement
        numbers     = "(?:(?:\s|^)-)?\d+[,.]?\d+?"
        celcius     = "°?(?:c|celcius|celsius|civili[sz]ed units?)"
        fahrenheit  = "°?(?:f|fahrenheit|freedom units?)"
        degrees     = "°?(?:d|deg|degrees?)"
        kelvin      = "[° ](?:k|kelvin)" # Space or ° mandatory so as not to confuse with k as in y2k (thousand).
        rankine     = "°?(?:r|rankine)"
        regex       = f"({numbers}) ?(?:({celcius})|({fahrenheit})|({degrees})|({kelvin})|({rankine}))(?:\s|$)"
        statement   = re.search(regex, text)
        if statement == None: return

        # Determine the origin unit.
        statement = statement.groups()
        temperature = float(statement[0].replace(",", "."))
        if   statement[1] != None: origin = 'c'
        elif statement[2] != None: origin = 'f'
        elif statement[3] != None: origin = 'd'
        elif statement[4] != None: origin = 'k'
        elif statement[5] != None: origin = 'r'

        # TODO Expand this with manual conversion options.
        # TODO Custom response if origin and dest temperatures are the same.
        if origin == 'd':   origin = 'c'
        if origin == 'c':   destination = 'f'
        else:               destination = 'c'

        # Calculate converted temperature
        dog_threshold = 35
        if   origin == 'c':
            new_temp    = self.celcius_table(temperature, destination)
            dog         = temperature >= dog_threshold;
        elif origin == 'f':
            new_temp    = self.fahrenheit_table(temperature, destination)
            dog         = self.fahrenheit_table(temperature, 'c') >= dog_threshold;
        elif origin == 'k':
            new_temp    = self.kelvin_table(temperature, destination)
            dog         = self.kelvin_table(temperature, 'c') >= dog_threshold;
        elif origin == 'r':
            new_temp    = self.rankine_table(temperature, destination)
            dog         = self.rankine_table(temperature, 'c') >= dog_threshold;
        if dog: image = discord.File("images/helldog.gif")
        else:   image = None

        new_temp = round(new_temp, 2)
        same_temperature = (temperature == new_temp)

        spotted = f"{author} I've spotted a temperature statement in your message!\n"
        origin = f"°{origin.upper()}"
        destination = f"°{destination.upper()}"
        if origin[1] == 'K': origin = origin[1]
        if destination[1] == 'K': destination = destination[1]

        if same_temperature:
            await channel.send(f"{spotted}And guess what! {temperature}{origin} is the same as {new_temp}{destination}! WOOOW!", file=image)
        else:
            await channel.send(f"{spotted}{temperature}{origin} is around {new_temp}{destination}", file=image)

        # TODO Remove debug print TODO
        print(statement)
        print(f"{temperature} {origin} {new_temp} {destination} {same_temperature}")

    def celcius_table(self, temp, dest):
        if   dest == 'c':   return temp
        elif dest == 'f':   return temp * 9.0 / 5.0 + 32
        elif dest == 'k':   return temp + 273.15
        elif dest == 'r':   return (temp + 273.15) * 9.0 / 5.0

    def fahrenheit_table(self, temp, dest):
        if   dest == 'c':   return (temp - 32) * 5.0 / 9.0
        elif dest == 'f':   return temp
        elif dest == 'k':   return (temp + 459.67) * 5.0 / 9.0
        elif dest == 'r':   return temp + 459.67

    def kelvin_table(self, temp, dest):
        if   dest == 'c':   return temp - 273.15
        elif dest == 'f':   return temp * 9.0 / 5.0 - 459.67
        elif dest == 'k':   return temp
        elif dest == 'r':   return temp * 9.0 / 5.0

    def rankine_table(self, temp, dest):
        if   dest == 'c':   return (temp - 491.67) * 5.0 / 9.0
        elif dest == 'f':   return temp - 469.67
        elif dest == 'k':   return temp * 5.0 / 9.0
        elif dest == 'r':   return temp

def setup(bot):
    bot.add_cog(MessageHandlerCog(bot))
