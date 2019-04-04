# This file is to avoid bloat in bot.py.
# It creates responses for various errors that may occur.
from discord.ext.commands.cooldowns import BucketType
from . import native
import inflect

def checkfailure(ctx, error):
    print (native.get_author(ctx) + 'tried to invoke command !' + str(ctx.command) + ' which resulted in a check failure.')

def cooldown(ctx, error):
    replystr = '%s The command **%s** can only be used %s every %s%s. Try again in %s.'
    # This replystr needs to have:
    #    author     Author mention
    #    cmd_name   Command name
    #    er_rate    error.cooldown.rate
    #    er_per     minutes and seconds interpretation of error.cooldown.per
    #    er_type    string interpretation of error.type
    #    er_retry   minutes and seconds interpretation of float error.retry_after

    author = ctx.author.mention
    cmd_name = ctx.message.content[0] + ctx.invoked_with # eg. !activity

    if error.cooldown.rate == 1:
        er_rate = 'once'
    elif error.cooldown.rate == 2:
        er_rate = 'twice'
    else:
        infl = inflect.engine()
        er_rate = infl.number_to_words(error.cooldown.rate) + ' times'

    er_per_sec = int(error.cooldown.per)
    er_retry_sec = int(error.retry_after)

    def seconds_parse(input):
        if input > 60:
            input_min = int(input / 60)
            input_sec = int(input - (input_min * 60))

            if input_sec != 0:
                output = ('%s min %s sec' % (str(input_min), str(input_sec)))
            else:
                output = ('%s min' % (str(input_min,) ))
        else:
            output = ('%s sec' % (str(input)))

        return output

    er_per = seconds_parse(er_per_sec)
    er_retry = seconds_parse(er_retry_sec)

    bucket = error.cooldown.type
    if bucket == BucketType.default:
        er_type = '' # Writing nothing is fine here.

    elif bucket == BucketType.user:
        er_type = ' by every user'

    elif bucket == BucketType.guild:
        er_type = ' in every server'

    elif bucket == BucketType.channel:
        er_type = ' in every channel'

    elif bucket == BucketType.member:
        er_type = ' by every user'

    else:
        er_type = ' [missing bucket type]'

    return (replystr % (author, cmd_name, er_rate, er_per, er_type, er_retry))
