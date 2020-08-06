"""Various helper methods for reading and writing to the database."""

import datetime
import sqlite3
from sqlite3 import Connection
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from mrfreeze.lib.colors import CYAN
from mrfreeze.lib.colors import CYAN_B
from mrfreeze.lib.colors import GREEN_B
from mrfreeze.lib.colors import RED
from mrfreeze.lib.colors import RED_B
from mrfreeze.lib.colors import RESET


class ExecutionResult:
    """Handy class for returning the result of db_execute."""

    def __init__(self, output: List[Any], error: Optional[Exception]) -> None:
        self.output = output
        self.error = error


def db_connect(dbpath: str) -> Connection:
    """Create a connection to a database."""
    return sqlite3.connect(dbpath)


def db_time(in_data: Union[str, datetime.datetime]) -> Optional[Union[str, datetime.datetime]]:
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


def db_execute(dbpath: str, sql: str, values: Tuple[Any, ...]) -> ExecutionResult:
    """Execute a database query."""
    error = None
    output = list()

    with db_connect(dbpath) as conn:
        c = conn.cursor()
        try:
            c.execute(sql, values)
            output = c.fetchall()
        except Exception as e:
            error = e

    return ExecutionResult(output, error)


def db_create(dbpath: str, dbname: str, table: str) -> None:
    """Create a database file from the provided tables."""
    conn = db_connect(dbpath)

    with conn:
        try:
            c = conn.cursor()
            c.execute(table)
            status =  f"{current_time()}{GREEN_B} Created {dbname}{RESET}"
            print(status)

        except sqlite3.Error as e:
            status =  f"{current_time()}{RED_B} Failed to create {dbname}\n{RED}{e}{RESET}"
            print(status)


def current_time() -> str:
    """Time stamps for database logging."""
    formated_time = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
    return f"{CYAN_B}{formated_time}{RESET}"


def success_print(module: str, message: str) -> None:
    """Log a successful database operation in a standardised fashion."""
    module = module.capitalize()
    print(f"{current_time()} {GREEN_B}{module}:{CYAN} {message}{RESET}")


def failure_print(module: str, message: str) -> None:
    """Log a failed database operation in a standardised fashion."""
    module = module.capitalize()
    print(f"{current_time()} {RED_B}{module}:{CYAN} {message}{RESET}")
