# This file is used for a number of smaller functions which are used two
# or more (perhaps many more) times in the bot.

import random

def mrfreeze():
    with open('config/mrfreezequotes', 'r') as f:
        return random.choice(f.read().strip().split('\n'))

def get_author(ctx):
    return str(ctx.author.name + '#' + str(ctx.author.discriminator) + ' ')

def get_image(desired):
    with open('config/files', 'r') as f:
        f = f.read().strip().split('\n')
        for i in f:
            if desired in i:
                return i.split(' ')[1]
        return 'https://i.imgur.com/pgNlDLT.png' # NoImage

def get_rule(rules):
    for i in range(len(rules)):
        rules[i] -= 1

    value = str()

    with open('config/rulesfile', 'r') as f:
        f = f.read().strip().split('\n')
        for i in rules:
            value += f[i]
            if rules[-1] != i:
                value += '\n'

    return value
