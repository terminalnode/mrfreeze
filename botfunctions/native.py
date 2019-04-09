# This file is used for a number of smaller functions which are used two
# or more (perhaps many more) times in the bot.

import re, datetime, discord
from . import userdb

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

def extract_time(args, fallback_minutes=True):
    # This function is used to extract time statements to know for how long
    # people are going to be muted, banned etc.
    default_duration = False
    args = ' '.join(args) + ' '

    # Keywords for individual time units.
    r_seconds   = 'seconds?|secs?|s[, ]'
    r_minutes   = 'minutes?|mins?|m[, ]'
    r_hours     = 'hours?|hrs?|h[, ]'
    r_days      = 'days?|d[, ]'
    r_weeks     = 'weeks?|w[, ]'
    r_months    = 'months?|mnth?s?|mons?'
    r_years     = 'years?|yrs?|y[, ]'

    # Combine them all into one regexp.
    r_time = ( '(\d+) ?((%s)|(%s)|(%s)|(%s)|(%s)|(%s)|(%s))' % (r_seconds, r_minutes, r_hours, r_days, r_weeks, r_months, r_years) )
    regex_output = re.findall(r_time, args, re.IGNORECASE)

    # The way the r_time regexp is designed it will output one tuple for every
    # time statement. Assuming a number was given the [0] and [1] will always
    # be non-empty, but the rest depend on the unit that was hit. So only
    # for seconds will [2] be nonempty, only for minutes will [3] be nonempty etc.
    time_dict = {
    'seconds' : [2,0],
    'minutes' : [3,0],
    'hours'   : [4,0],
    'days'    : [5,0],
    'weeks'   : [6,0],
    'months'  : [7,0],
    'years'   : [8,0]
    }

    for unit in time_dict:
        unit_index = time_dict[unit][0]
        for hit in regex_output:
            if hit[unit_index] != '' and hit[0] != '':
                time_dict[unit][1] += int(hit[0])

    # Now we'll remove all the indexes from the time dict as they're no longer needed.
    for unit in time_dict:
        time_dict[unit] = time_dict[unit][1]

    # Now we'll put all of this time into a datetime.datetime object.
    # Because we can't use months and years precisely these will be converted to
    # 30 and 365 days respectively.
    current_date = datetime.datetime.now()
    add_time = datetime.timedelta(days=(time_dict['days'] + (time_dict['months']*30) + (time_dict['years']*365)), weeks=time_dict['weeks'],
                                  hours=time_dict['hours'], minutes=time_dict['minutes'], seconds=time_dict['seconds'])
    end_date = current_date + add_time

    # If nothing was detected, we'll look for isolated integers, add them all
    # up and assume those are minutes. Then remove them from the reply string.
    if (end_date == current_date) and fallback_minutes:
        resplit = args.split(' ')
        int_list = list()

        # Finding integers
        for arg in resplit:
            if arg.isdigit():
                int_list.append(int(arg))

        # Removing integers from original args and summing up minutes.
        # Using re to know if there're spaces to remove as well.
        no_minutes = 0
        for number in int_list:
            regexp = (' ?%s' % (str(number),))
            re_results = re.findall(regexp, args)
            for hit in re_results:
                args = args.replace(hit, '')
            no_minutes += number

        # Finally creating the new add_time and end_date.
        if no_minutes > 0:
            add_time = datetime.timedelta(minutes = no_minutes)
            end_date = current_date + add_time


    if end_date == current_date:
        # In this scenario, no time statements have been found.
        end_date = None

    # Finally, we're going to remove all the time expressions from the args we got.
    r_list = [r_seconds, r_minutes, r_hours, r_days, r_weeks, r_months, r_years]
    for unit in r_list:
        matches = re.findall(('(\d+ ?(%s))' % unit), args, re.IGNORECASE)
        for match in matches:
            args = args.replace(match[0], '')

    # Finally we can return our values.
    return args, add_time, end_date

def parse_timedelta(time_delta):
    # This function takes a time delta as it's argument and outputs
    # a string such as "1 days, 2 hours, 3 minutes and 4 seconds".

    # Time delta only gives us days and seconds, we have to calculate
    # hours and minutes ourselves.
    days = time_delta.days
    seconds = time_delta.seconds

    # Some simple calculations. Weeks are the last whole number we can get from
    # days/7 i.e. int(days/7), then weeks*7 are subtracted from the remanining days
    # and so on and so on for hours and minutes.
    weeks = int(days / 7)
    days = (days - (weeks * 7))
    hours = int(seconds / 3600)
    seconds = (seconds - (hours * 3600))
    minutes = int(seconds / 60)
    seconds = (seconds - (minutes * 60))

    time_str = ''
    size_order = ( ('week', weeks), ('day', days), ('hour', hours), ('minute', minutes), ('second', seconds) )

    for value in range(len(size_order)):
        # Number of trailing values are used to know if we should
        # add an 'and' after the value.
        trailing_values = 0

        # Checking that this isn't the last value.
        if value != (len(size_order) - 1):

            # Going through all trailing values and checking which are non-zero.
            for i in size_order[value+1:]:
                if i[1] > 0:
                    trailing_values += 1

        # Adding the value to the string if it's more than zero.
        if size_order[value][1] > 0:
            if size_order[value][1] == 1:
                time_str += str(size_order[value][1]) + ' ' + size_order[value][0]
            else:
                time_str += str(size_order[value][1]) + ' ' + size_order[value][0] + 's'

            if trailing_values == 0:
                pass
            elif trailing_values == 1:
                time_str += ' and '
            else:
                time_str += ', '

    return time_str

async def punish_banish(ctx):
    # The user has angered the gods by using a command reserved for mods.
    # They will be banished to Antarctica for fifteen minutes.

    current_time = datetime.datetime.now()
    duration = datetime.timedelta(minutes=15)
    end_time = current_time + duration

    try:
        await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name='Antarctica'))
        prolonged = userdb.prolong_mute(ctx.author, until=end_time)
        succeeded = True
    except:
        succeeded = False

    if not prolonged:
        replystr = '%s You ignorant smud, you want banish? I\'ll give you banish... '
        replystr += '15 whole minutes of it! :rage:'
        replystr = (replystr % (ctx.author.mention,))

    else:
        replystr = '%s You don\'t have the power to banish, only to be banished... '
        replystr += 'but it seems you already know that. Your sentence has been '
        replystr += '***extended*** by 15 minutes!'
        replystr = (replystr % (ctx.author.mention,))

    if succeeded:
        await ctx.send(replystr)
