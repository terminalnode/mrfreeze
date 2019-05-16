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

        # Look for temperature statements and autoconvert them.
        ctx = await self.bot.get_context(message)
        await self.temperatures(ctx)

    async def temperatures(self, ctx):
        # Trailing space is required for matching temperatures at the end of the message.
        author = ctx.author.mention
        roles = ctx.author.roles
        channel = ctx.channel

        # Abort if no temperature statement was found.
        statement = self.parse_request(ctx.message.content)
        if not statement: return

        # Check if input is ridiculous.
        if abs(statement['temperature']) > 100000:
            await channel.send(f'{author} No matter what unit you put that in the answer is still gonna be "quite warm".')
            return

        # Calculate converted temperature, see if it's above or equal to dog threshold.
        dog_threshold = 35 # defined in celcius
        if   statement['origin'] == 'c':
            new_temp    = self.celcius_table(statement['temperature'], statement['destination'])
            dog         = statement['temperature'] >= dog_threshold;

        elif statement['origin'] == 'f':
            new_temp    = self.fahrenheit_table(statement['temperature'], statement['destination'])
            dog         = self.fahrenheit_table(statement['temperature'], 'c') >= dog_threshold;

        elif statement['origin'] == 'k':
            new_temp    = self.kelvin_table(statement['temperature'], statement['destination'])
            dog         = self.kelvin_table(statement['temperature'], 'c') >= dog_threshold;

        elif statement['origin'] == 'r':
            new_temp    = self.rankine_table(statement['temperature'], statement['destination'])
            dog         = self.rankine_table(statement['temperature'], 'c') >= dog_threshold;

        if dog: image = discord.File("images/helldog.gif")
        else:   image = None

        old_temp = statement['temperature']
        new_temp = round(new_temp, 2)
        no_change = (old_temp == new_temp)
        same_unit = (statement['origin'] == statement['destination'])

        # Kelvin isn't supposed to have a ° before it, all others should.
        origin      = f"°{statement['origin'].upper()}".replace("°K", "K")
        destination = f"°{statement['destination'].upper()}".replace("°K", "K")

        # Time for the reply.
        if no_change:
            if same_unit and statement['manual']:
                reply = f"Did {author} just try to convert {old_temp}{origin} to {destination}? :thinking:"
            elif statement['manual']:
                reply = f"Uh... {old_temp}{origin} is the same in {new_temp}{destination} you smud. :angry:"
            else:
                reply = f"Guess what! {old_temp}{origin} is the same as {new_temp}{destination}! WOOOW!"
        else:             reply = f"{old_temp}{origin} is around {new_temp}{destination}"
        await channel.send(reply, file=image)

    def parse_request(self, text):
        """Extract temperature statement from text.
        If no temperature statement is found returns false.
        Otherwise returns a dictionary with keys: temperature, origin, destination, manual"""
        # Space or ° mandatory for kelvin to avoid collision with k as in thousand.
        numbers    = "(?:(?:\s|^)-)?\d+(?:[,.]\d+)? ?"
        celcius    = "°?(?:c|celcius|celsius|civili[sz]ed units?)"
        fahrenheit = "°?(?:f|fahrenheit|freedom units?)"
        degrees    = "°?(?:deg|degrees)"
        kelvin     = "(?:k|kelvin)"
        rankine    = "°?(?:r|rankine)"
        regex      = f"({numbers})(?:({celcius})|({fahrenheit})|([ °]{kelvin})|({rankine})|({degrees}))(?:\s|$)"
        statement  = re.search(regex, text, re.IGNORECASE)
        if not statement: return False

        result = dict()

        # Determine the origin unit.
        statement = statement.groups()
        result['temperature'] = float(statement[0].replace(",", "."))
        if   statement[1]: result['origin'] = 'c'
        elif statement[2]: result['origin'] = 'f'
        elif statement[3]: result['origin'] = 'k'
        elif statement[4]: result['origin'] = 'r'

        # Origin is "degrees", turning it into a real unit.
        # TODO Better origin-guessing.
        elif statement[5]:
            result['origin'] = 'c'

        # Determine destination unit
        # First we'll look for force conversions
        no_catch = f"(?:(?:{numbers}) ?(?:{celcius}|{fahrenheit}|{degrees}|[ °]{kelvin}|{rankine})) (?:for|in|as|(?:convert )?to|convert)"
        find_convert = f"{no_catch} (?:({celcius})|({fahrenheit})|(°?{kelvin})|({rankine}))(?:\s|$)"
        conversion = re.search(find_convert, text, re.IGNORECASE)

        if conversion:
            result['manual'] = True
            conversion = conversion.groups()
            if   conversion[0]: result['destination'] = 'c'
            elif conversion[1]: result['destination'] = 'f'
            elif conversion[2]: result['destination'] = 'k'
            elif conversion[3]: result['destination'] = 'r'
        else:
            # TODO Better destination-guessing.
            result['manual'] = False
            if result['origin'] == 'c': result['destination'] = 'f'
            else:                       result['destination'] = 'c'

            # TODO Remove debug print TODO
            print(statement)
            print(f"{result['temperature']} {result['origin']} to {result['destination']}. Manual: {result['manual']}")

        return result

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
