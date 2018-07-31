import discord, re
from discord.ext import commands

async def convert(ctx, tempstatement):
    tempstatement = tempstatement.group()
    # The origin temperature will be a float number.
    # The origin unit will be a single letter corresponding to:
    # (d)egrees, (f)ahrenheit, (k)elvin, (c)elcius, (r)ankine
    origin_temp   = float(re.match('-?\d+[,.]?\d+', tempstatement).group().replace(',','.'))
    origin_unit   = re.search('[a-z]', tempstatement).group()

    # If the origin unit is unspecified (degrees) we'll look at the users
    # regional tags to determine if they're in North America or elsewhere.
    # This will make an educated guess as to what unit they meant.
    if origin_unit == 'd':
        origin_unit = 'c'
        for i in ctx.author.roles:
            if i.name == 'North America':
                origin_unit = 'f'

    # We'll need some conversion tables to convert between the different temperatures.
    # These function take the unit in their name and convert it to the unit in 'dest'.
    def celcius_table(temp, dest):
        if dest == 'f':
            return temp * 9.0 / 5.0 + 32
        elif dest == 'k':
            return temp + 273.15
        elif dest == 'r':
            return (temp + 273.15) * 9.0 / 5.0

    def fahrenheit_table(temp, dest):
        if dest == 'c':
            return (temp - 32) * 5.0 / 9.0
        elif dest == 'k':
            return (temp + 459.67) * 5.0 / 9.0
        elif dest == 'r':
            return temp + 459.67

    def kelvin_table(temp, dest):
        if dest == 'c':
            return temp - 273.15
        elif dest == 'f':
            return temp * 9.0 / 5.0 - 459.67
        elif dest == 'r':
            return temp * 9.0 / 5.0

    def rankine_table(temp, dest):
        if dest == 'c':
            return (temp - 491.67) * 5.0 / 9.0
        elif dest == 'f':
            return temp - 469.67
        elif dest == 'k':
            return temp * 5.0 / 9.0

    # For now we'll just convert between C and F, later on
    # we'll add an option to convert to the other temperatures.
    if origin_unit == 'c':
        dest_unit = 'f'
    elif origin_unit == 'f':
        dest_unit = 'c'
    else:
        dest_unit = 'c'

    # Now let's convert the temperature.
    if origin_unit == 'c':
        dest_temp = celcius_table(origin_temp, dest_unit)
    elif origin_unit == 'f':
        dest_temp = fahrenheit_table(origin_temp, dest_unit)
    elif origin_unit == 'k':
        dest_temp = kelvin_table(origin_temp, dest_unit)
    elif origin_unit == 'r':
        dest_temp = rankine_table(origin_temp, dest_unit)

    # Let's round the numbers, both of them to be safe.
    origin_temp = str(round(origin_temp, 2))
    dest_temp   = str(round(dest_temp, 2))

    reply = (ctx.author.mention + ' I\'ve spotted a temperature statement in your message!\n' +
            origin_temp + '°' + origin_unit.upper() + ' is equal to ' +
            dest_temp   + '°' + dest_unit.upper() + '.')

    await ctx.send(reply)
