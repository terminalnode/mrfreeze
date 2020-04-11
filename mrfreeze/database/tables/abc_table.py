"""Abstract base class for settings."""

import logging
import sqlite3
from abc import ABCMeta
from typing import Dict
from typing import Optional
from typing import Union

from discord import Guild
from discord import Role
from discord import TextChannel

from mrfreeze.colors import GREEN, MAGENTA, RED, RESET, YELLOW_B

from ..helpers import db_connect
from ..helpers import db_execute


class ABCTable(metaclass=ABCMeta):
    """
    Abstract base class for Settings.

    This class defines a number of properties that every settings submodule
    needs to be able to interface properly with the rest of the system.
    """

    # General properties
    name: str
    table_name: str
    dict: Optional[Dict[int, Union[bool, int]]]
    dbpath: str
    logger: logging.Logger

    # SQL commands
    select_all: str
    insert: str
    table: str

    def create_table(self) -> None:
        """Create the table for a given module."""
        conn = db_connect(self.dbpath)

        with conn:
            try:
                c = conn.cursor()
                c.execute(self.table)
                self.infolog("created database table")

            except sqlite3.Error as e:
                self.errorlog(f"failed to create database table: {e}")

    def load_from_db(self) -> None:
        """
        Load the values of a given modules from database into memory.

        Each module has a dictionary called self.dict into which the values
        are all loaded. This function generalises this process so it doesn't
        have to be implemented into all the cogs individually.
        """
        query = db_execute(self.dbpath, self.select_all, tuple())

        if query.error is None:
            new_dict = dict()
            for entry in query.output:
                new_dict[entry[0]] = entry[1]

            self.dict = new_dict
            self.infolog(f"successfully fetched data")
        else:
            self.errorlog(f"failed to fetch data: {query.error}")
            self.dict = None

    def get(self, server: Guild) -> Optional[int]:
        """Get the value from a given module for a given server."""
        # Check that values are loaded, if not try again.
        if self.dict is None:
            self.load_from_db()

        # Check that they loaded properly, otherwise return None.
        if self.dict is None:
            return None

        # Check if requested server has an entry, otherwise return None.
        if server.id not in self.dict:
            return None

        # Finally, return the actual value from the dictionary.
        return self.dict[server.id]

    def update_dictionary(self, key: int, value: Union[int, bool]) -> bool:
        """Update the dictionary for a given module."""
        if self.dict is None:
            self.load_from_db()

        if self.dict is None:
            return False
        else:
            self.dict[key] = value
            return True

    def set(self, object: Union[TextChannel, Role]) -> bool:
        """Set the value using a TextChannel or Role object."""
        return self.upsert(object.guild, object.id)

    def set_by_id(self, server: Guild, value: Union[bool, int]) -> bool:
        """Set the value using a Guild object and a value."""
        return self.upsert(server, value)

    def upsert(self, server: Guild, value: Union[int, bool]) -> bool:
        """Insert or update the value for `server.id` with `value`."""
        query = db_execute(self.dbpath, self.insert, (server.id, value, value))

        if query.error is not None:
            self.errorlog(
                f"failed to set {server.name} to {value}\n{query.error}")
            return False

        elif not self.update_dictionary(server.id, value):
            self.errorlog(
                f"failed to update dictionary for {server.name} to {value}\n{query.error}")
            return False

        else:
            self.infolog(
                f"set {server.name} to {value}")
            return True

    def infolog(self, msg: str) -> None:
        """Write a message to the log, prefixing it with the module name."""
        self.logger.info(f"{YELLOW_B}{self.name} {GREEN}{msg}{RESET}")

    def warnlog(self, msg: str) -> None:
        """Write a message to the log, prefixing it with the module name."""
        self.logger.info(f"{YELLOW_B}{self.name} {RED}{msg}{RESET}")

    def errorlog(self, msg: str) -> None:
        """Write a message to the log, prefixing it with the module name."""
        self.logger.info(f"{YELLOW_B}{self.name} {MAGENTA}{msg}{RESET}")
