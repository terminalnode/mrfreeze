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

        ctx = await self.bot.get_context(message)

        # Look for temperature statements and autoconvert them.
        await self.temperatures(ctx)

    async def temperatures(self, ctx):
        # Trailing space is required for matching temperatures at the end of the message.
        text = ctx.message.content
        author = ctx.author.mention
        roles = ctx.author.roles
        channel = ctx.channel

        # Extract temperature statement
        # Space or ° mandatory for kelvin to avoid collision with k as in thousand.
        numbers    = "(?:(?:\s|^)-)?\d+(?:[,.]\d+)? ?"
        celcius    = "°?(?:c|celcius|celsius|civili[sz]ed units?)"
        fahrenheit = "°?(?:f|fahrenheit|freedom units?)"
        degrees    = "°?(?:deg|degrees)"
        kelvin     = "(?:k|kelvin)"
        rankine    = "°?(?:r|rankine)"
        regex      = f"({numbers})(?:({celcius})|({fahrenheit})|([ °]{kelvin})|({rankine})|({degrees}))(?:\s|$)"
        statement  = re.search(regex, text, re.IGNORECASE)
        # Abort if no temperature statement was found.
        if not statement: return

        # Determine the origin unit.
        statement = statement.groups()
        temperature = float(statement[0].replace(",", "."))
        if   statement[1]: origin = 'c'
        elif statement[2]: origin = 'f'
        elif statement[3]: origin = 'k'
        elif statement[4]: origin = 'r'

        # Origin is "degrees", turning it into a real unit.
        # TODO Better origin-guessing.
        elif statement[5]:
            origin = 'c'

        # Determine destination unit
        # First we'll look for force conversions
        no_catch = f"(?:(?:{numbers}) ?(?:{celcius}|{fahrenheit}|{degrees}|[ °]{kelvin}|{rankine})) (?:for|in|as|(?:convert )?to|convert)"
        find_convert = f"{no_catch} (?:({celcius})|({fahrenheit})|(°?{kelvin})|({rankine}))(?:\s|$)"
        conversion = re.search(find_convert, text, re.IGNORECASE)

        if conversion:
            manual = True
            conversion = conversion.groups()
            if   conversion[0]: destination = 'c'
            elif conversion[1]: destination = 'f'
            elif conversion[2]: destination = 'k'
            elif conversion[3]: destination = 'r'
        else:
            # TODO Better destination-guessing.
            manual = False
            if origin == 'c': destination = 'f'
            else:             destination = 'c'

            # TODO Remove debug print TODO
            print(statement)
            print(f"{temperature} {origin} to {destination}. Manual: {manual}")

        # Calculate converted temperature, see if it's above or equal to dog threshold.
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
        no_change = (temperature == new_temp)
        same_unit = (origin == destination)

        # Kelvin isn't supposed to have a ° before it, all others should.
        origin      = f"°{origin.upper()}".replace("°K", "K")
        destination = f"°{destination.upper()}".replace("°K", "K")

        # Time for the reply.
        if no_change:
            if same_unit and manual:
                reply = f"Did {author} just try to convert {temperature}{origin} to {destination}? :thinking:"
            elif manual:
                reply = f"Uh... {temperature}{origin} is the same in {new_temp}{destination} you smud. :angry:"
            else:
                reply = f"Guess what! {temperature}{origin} is the same as {new_temp}{destination}! WOOOW!"
        else:             reply = f"{temperature}{origin} is around {new_temp}{destination}"
        await channel.send(reply, file=image)

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
        in_celcius = ( temp - 273.15 )
        return self.celcius_table( in_celcius, dest )

    def rankine_table(self, temp, dest):
        in_fahrenheit = ( temp - 459.67 )
        return self.fahrenheit_table( in_fahrenheit, dest )

def setup(bot):
    bot.add_cog(MessageHandlerCog(bot))
