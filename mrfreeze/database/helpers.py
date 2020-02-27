import datetime
import sqlite3

from mrfreeze.colors import CYAN, CYAN_B, GREEN_B, RED_B, RESET

class ExecutionResult:
    """Handy class for returning the result of db_execute."""
    def __init__(self, output, error):
        self.output = output
        self.error = error

def db_connect(dbpath):
    """Create a connection to a database."""
    conn = sqlite3.connect(dbpath)
    return conn


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

def db_execute(dbpath, sql, values):
    """Execute a database query."""
    error = None
    output = None

    with db_connect(dbpath) as conn:
        c = conn.cursor()
        try:
            c.execute(sql, values)
            output = c.fetchall()
        except Exception as e:
            error = e

    return ExecutionResult(output, error)


def db_create(dbpath, dbname, table, comment=None):
    """Create a database file from the provided tables."""
    conn = db_connect(dbpath)

    log_message = dbname
    if comment is not None:
        log_message = f"{dbname} ({comment})"

    with conn:
        try:
            c = conn.cursor()
            c.execute(table)
            print(f"{CYAN}DB/table created: " +
                  f"{GREEN_B}{log_message}{RESET}")

        except sqlite3.Error as e:
            print(e)
            print(f"{CYAN}DB/table failure: " +
                  f"{RED_B}{log_message}\n{e}{RESET}")


def current_time():
    """Time stamps for database logging."""
    formated_time = datetime.datetime.strftime(
            datetime.datetime.now(),
            "%Y-%m-%d %H:%M"
    )
    return f"{CYAN_B}{formated_time}{RESET}"

def success_print(module, message):
    """Standardised way of logging a successful database operation"""
    print(f"{current_time()} {GREEN_B}{module}:{CYAN} {message}{RESET}")


def failure_print(module, message):
    """Standardised way of logging a failed database operation"""
    print(f"{current_time()} {RED_B}{module}:{CYAN} {message}{RESET}")
