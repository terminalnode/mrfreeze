"""
Helper methods  for database interractions.

A simple module containing some helper methods
for handling interraction with databases.
"""
import datetime
import sqlite3

from mrfreeze import colors


def db_connect(bot, dbname):
    """Create a connection to a database."""
    db_file = f"{bot.db_prefix}/{dbname}.db"
    conn = sqlite3.connect(db_file)
    return conn


def db_create(bot, dbname, tables, comment=None):
    """Create a database file from the provided tables."""
    conn = bot.db_connect(bot, dbname)
    if comment is not None:
        dbname = f"{dbname} ({comment})"

    with conn:
        try:
            c = conn.cursor()
            c.execute(tables)
            print(f"{colors.CYAN}DB/table created: " +
                  f"{colors.GREEN_B}{dbname}{colors.RESET}")

        except sqlite3.Error as e:
            print(f"{colors.CYAN}DB/table failure: " +
                  f"{colors.RED_B}{dbname}\n{str(e)}{colors.RESET}")


def db_time(in_data):
    """
    Parse to and from datetime objects consistently for database use.

    A datetime object is parsed to a string.
    A string is parsed to a datetime object.
    Anything else returns None.
    """
    timeformat = "%Y-%m-%d %H:%M:%S"

    if isinstance(in_data, datetime.datetime):
        return datetime.datetime.strftime(in_data, timeformat)
    elif isinstance(in_data, str):
        return datetime.datetime.strptime(in_data, timeformat)
    else:
        return None
