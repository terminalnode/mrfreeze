# This file is used for a number of smaller functions which are used two
# or more (perhaps many more) times in the bot.

import random, re, datetime

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

def extract_time(args):
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

    # Finally, we're going to remove all the time expressions from the args we got.
    r_list = [r_seconds, r_minutes, r_hours, r_days, r_weeks, r_months, r_years]
    for unit in r_list:
        matches = re.findall(('(\d+ ?(%s))' % unit), args, re.IGNORECASE)
        for match in matches:
            args = args.replace(match[0], '')

    # Finally we can return our values.
    return args, add_time, end_date
