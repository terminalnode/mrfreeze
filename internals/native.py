# This file is used for a number of smaller functions which are used two
# or more (perhaps many more) times in the bot.

import re, datetime, discord
from databases import mutes

def get_author(ctx):
    return str(ctx.author.name + '#' + str(ctx.author.discriminator) + ' ')
def get_trash_channel(guild):
    """Currently just gives the channel with the name bot-trash.
    In the future this may be expanded so servers can designate whatever channel they want as Antarctica."""
    for channel in guild.text_channels:
        if channel.name.lower() == "bot-trash":
            return channel
    return None

def get_antarctica_role(guild):
    """Currently just gives the role with the name antarctica.
    In the future this may be expanded so servers can designate whatever role they want as Antarctica."""
    for role in guild.roles:
        if role.name.lower() == "antarctica":
            return role
    return None

def get_antarctica_channel(guild):
    """Currently just gives the channel with the name antarctica.
    In the future this may be expanded so servers can designate whatever channel they want as Antarctica."""
    for channel in guild.text_channels:
        if channel.name.lower() == "antarctica":
            return channel
    return None

def get_image(desired):
    with open('config/files', 'r') as f:
        f = f.read().strip().split('\n')
        for i in f:
            if desired in i:
                return i.split(' ')[1]
        return 'https://i.imgur.com/pgNlDLT.png' # NoImage


def mentions_list(mentions):
    """Create a string of mentions from a list of user objects."""
    mentions = [ user.mention for user in mentions ]
    if len(mentions) == 0:      return "No one"
    elif len(mentions) == 1:    return mentions[0]
    else:                       return ", ".join(mentions[:-1]) + f" and {mentions[-1]}"

def extract_time(args, fallback_minutes=True):
    """Extract time expressions from a set of arguments.
    If time expressions are not found, assume all digits refer to minutes.

    Return a timedelta and an end time if successful, otherwise (None, None)."""

    # Create regular expression
    seconds   = 'seconds?|secs?|s[, ]'
    minutes   = 'minutes?|mins?|m[, ]'
    hours     = 'hours?|hrs?|h[, ]'
    days      = 'days?|d[, ]'
    weeks     = 'weeks?|w[, ]'
    months    = 'months?|mnth?s?|mons?'
    years     = 'years?|yrs?|y[, ]'
    find_time = f"(\d+) ?(({seconds})|({minutes})|({hours})|({days})|({weeks})|({months})|({years}))"

    regex_output = re.findall(
            find_time,      # Use our newly created regex.
            ' '.join(args), # Search through the arguments.
            re.IGNORECASE)   # Ignore case when applying the expression.

    # Sum up all hits for the different time units
    time_dict = {
    'seconds' : sum( [ int(row[0]) for row in regex_output if row[2] != '' ] ),
    'minutes' : sum( [ int(row[0]) for row in regex_output if row[3] != '' ] ),
    'hours'   : sum( [ int(row[0]) for row in regex_output if row[4] != '' ] ),
    'days'    : sum( [ int(row[0]) for row in regex_output if row[5] != '' ] ),
    'weeks'   : sum( [ int(row[0]) for row in regex_output if row[6] != '' ] ),
    'months'  : sum( [ int(row[0]) for row in regex_output if row[7] != '' ] ),
    'years'   : sum( [ int(row[0]) for row in regex_output if row[8] != '' ] ),
    }

    # Create a new datetime object based on these numbers.
    # Months and years are converted to 30 and 365 days respectively.
    add_time = datetime.timedelta(
            days    =   time_dict['days'] + (time_dict['months'] * 30) + (time_dict['years'] * 365),
            weeks   =   time_dict['weeks'],
            hours   =   time_dict['hours'],
            minutes =   time_dict['minutes'],
            seconds =   time_dict['seconds'])
    current_date = datetime.datetime.now()
    end_date = current_date + add_time

    # If nothing was found, assume all numbers are minutes.
    if (end_date == current_date) and fallback_minutes:
        no_minutes = sum([ int(arg) for arg in args if arg.isdigit() ])
        add_time = datetime.timedelta(minutes = no_minutes)
        end_date = current_date + add_time

    # Return None if current date and end date are different.
    if end_date != current_date:
        return add_time, end_date
    else:
        return None, None

def parse_timedelta(time_delta):
    # This function takes a time delta as it's argument and outputs
    # a string such as "1 days, 2 hours, 3 minutes and 4 seconds".

    if time_delta == None:
        return "an eternity"

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
