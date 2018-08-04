# This file is used for a number of smaller functions which are used two
# or more (perhaps many more) times in the bot.

import random

def mrfreeze():
    with open('config/mrfreezequotes', 'r') as f:
        return random.choice(f.read().strip().split('\n'))

def get_author(ctx):
    return str(ctx.author.name + '#' + str(ctx.author.discriminator) + ' ')
