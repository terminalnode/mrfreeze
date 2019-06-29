import sqlite3
import datetime

def db_connect(bot, dbname):
    """Creates a connection to the regionbl database."""
    db_file = f'{bot.db_prefix}/{dbname}.db'
    conn = sqlite3.connect(db_file)
    return conn

def db_create(bot, dbname, tables):
    """Create a database file from the provided tables."""
    conn = bot.db_connect(bot, dbname)
    with conn:
        try:
            c = conn.cursor()
            c.execute(tables)
            print(f'{bot.CYAN}DB created: {bot.GREEN_B}{dbname}{bot.RESET}')

        except sqlite3.Error as e:
            print(f'{bot.CYAN}DB failure: {bot.RED_B}{dbname}\n{str(e)}{bot.RESET}')

def db_time(in_data):
    """Pase datetime to string, string to datetime and everything else to None."""
    timeformat = "%Y-%m-%d %H:%M:%S"

    if isinstance(in_data, datetime.datetime):
        return datetime.datetime.strftime(in_data, timeformat)
    elif isinstance(in_data, str):
        return datetime.datetime.strptime(in_data, timeformat)
    else:
        return None
