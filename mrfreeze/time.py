"""Module for converting text to timedelta objects and vice versa."""
import datetime
import re


def extract_time(args, fallback_minutes=True):
    """
    Extract time expressions from a set of arguments.

    If time expressions are not found, assume all digits refer to minutes.
    Return a timedelta and an end time if successful, otherwise (None, None).
    """
    # Create regular expression
    seconds = r"seconds?|secs?|s[, ]"
    minutes = r"minutes?|mins?|m[, ]"
    hours = r"hours?|hrs?|h[, ]"
    days = r"days?|d[, ]"
    weeks = r"weeks?|w[, ]"
    months = r"months?|mnth?s?|mons?"
    years = r"years?|yrs?|y[, ]"
    find_time = (fr"(-?\d+) ?(({seconds})|({minutes})|({hours})" +
                 fr"|({days})|({weeks})|({months})|({years}))")

    regex_output = re.findall(
            find_time,       # Use our newly created regex.
            " ".join(args),  # Search through the arguments.
            re.IGNORECASE)   # Ignore case when applying the expression.

    # Sum up all hits for the different time units
    time_dict = {
        "seconds": sum([int(row[0]) for row in regex_output if row[2]]),
        "minutes": sum([int(row[0]) for row in regex_output if row[3]]),
        "hours": sum([int(row[0]) for row in regex_output if row[4]]),
        "days": sum([int(row[0]) for row in regex_output if row[5]]),
        "weeks": sum([int(row[0]) for row in regex_output if row[6]]),
        "months": sum([int(row[0]) for row in regex_output if row[7]]),
        "years": sum([int(row[0]) for row in regex_output if row[8]]),
    }

    # Create a new datetime object based on these numbers.
    # Months and years are converted to 30 and 365 days respectively.
    time_dict["days"] += ((time_dict["months"] * 30) +
                          (time_dict["years"] * 365))
    current_time = datetime.datetime.now()

    try:
        add_time = datetime.timedelta(
            weeks=time_dict["weeks"],
            days=time_dict["days"],
            hours=time_dict["hours"],
            minutes=time_dict["minutes"],
            seconds=time_dict["seconds"])
        end_date = current_time + add_time

        # If nothing was found, assume all numbers are minutes.
        if (end_date == current_time) and fallback_minutes:
            no_minutes = sum([int(arg) for arg in args if arg.isdigit()])
            add_time = datetime.timedelta(minutes=no_minutes)
            end_date = current_time + add_time

    except OverflowError:
        # If overflowing, just set the end_date to maximum.
        end_date = datetime.datetime.max
        add_time = end_date - current_time

    # Return None if current date and end date are different.
    if end_date != current_time:
        return add_time, end_date
    else:
        return None, None


def parse_timedelta(time_delta):
    """Convert a timedelta object to a string such as '1 day, 2 hours[...]'."""
    # This function takes a time delta as it's argument and outputs
    # a string such as "1 days, 2 hours, 3 minutes and 4 seconds".

    if time_delta is None:
        return "an eternity"

    # Time delta only gives us days and seconds, we have to calculate
    # hours and minutes ourselves.
    days = time_delta.days
    seconds = time_delta.seconds
    microseconds = time_delta.microseconds

    # Some simple calculations. Weeks are the last whole number we can get from
    # days/7 i.e. int(days/7), then weeks*7 are subtracted from the remanining
    # days and so on and so on for hours and minutes.
    weeks = int(days / 7)
    days = (days - (weeks * 7))
    hours = int(seconds / 3600)
    seconds = (seconds - (hours * 3600))
    minutes = int(seconds / 60)
    seconds = round((seconds - minutes * 60 + microseconds / 1000000))

    time_str = ""
    size_order = (
        ("week", weeks), ("day", days),
        ("hour", hours), ("minute", minutes),
        ("second", seconds)
    )

    for value in range(len(size_order)):
        # Number of trailing values are used to know if we should
        # add an 'and' after the value.
        trailing_values = 0

        # Checking that this isn't the last value.
        if value != (len(size_order) - 1):

            # Going through all trailing values and
            # checking which are non-zero.
            for i in size_order[value+1:]:
                if i[1] > 0:
                    trailing_values += 1

        # Adding the value to the string if it's more than zero.
        if size_order[value][1] > 0:
            if size_order[value][1] == 1:
                time_str += f"(size_order[value][1]) {size_order[value][0]}"
            else:
                time_str += f"{size_order[value][1]} {size_order[value][0]}s"

            if trailing_values == 0:
                pass
            elif trailing_values == 1:
                time_str += " and "
            else:
                time_str += ", "
    return time_str
