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

def mentions_list(mentions):
    text_list = str()

    if len(mentions) == 0:
        text_list = 'No one.'

    elif len(mentions) == 1:
        text_list = mentions[0].mention

    else:
        for i in range(len(mentions)):
            if i != (len(mentions)-1):
                if i == 0:
                    text_list += (mentions[i].mention)
                else:
                    text_list += (', ' + mentions[i].mention)
            else:
                text_list += (' and ' + mentions[i].mention)

    return text_list
