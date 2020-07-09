"""Abstract base class for settings."""

import logging
import sqlite3
from abc import ABCMeta
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import Tuple

from mrfreeze.database.helpers import db_connect
from mrfreeze.database.helpers import db_execute
from mrfreeze.lib.colors import GREEN
from mrfreeze.lib.colors import MAGENTA
from mrfreeze.lib.colors import RED
from mrfreeze.lib.colors import RESET
from mrfreeze.lib.colors import YELLOW_B


class ABCTableBase(metaclass=ABCMeta):
    """
    Abstract base class for Tables.

    This class defines a number of properties that every table submodule
    needs to have to be able to interface properly with the rest of the system.
    """

    # General properties
    name: str
    table_name: str
    dbpath: str
    logger: logging.Logger
    primary_keys: Tuple[str]
    secondary_keys: Tuple[str]

    # SQL commands
    select_all: str
    insert: str
    table: str

    # Functions
    @abstractmethod
    def upsert(self, key: Any, value: Any) -> bool:
        """
        Insert or update something into the database.

        This is the old upsert method which is overridden in the various subclasses.
        """
        pass

    @abstractmethod
    def load_from_db(self) -> None:
        """Load all data from the database into memory."""
        pass

    def update(self, pairs: Dict[Any, Any], accept_none: bool = False) -> bool:
        """
        Update (or insert) something into the database.

        This is a new method replacing the old upsert. The main difference is
        how the operation is carried out. Each table will have a set of primary
        and a set of secondary keys. The primary keys are basically the primary
        keys of the table, used for the ON CONFLICT part of the insert.

        The function never accepts None in the primary keys, and also doesn't
        accept None is secondary keys unless accept_none is set to True.
        """
        primary_values = tuple([ pairs[v] for v in self.primary_keys ])
        secondary_values = tuple([ pairs[v] for v in self.secondary_keys ])
        value_fill = primary_values + secondary_values + secondary_values

        # Check that all required values are filled in
        if None in primary_values or (not accept_none and None in secondary_values):
            self.errorlog(
                "missing one or more values, can't upsert")
            return False
        else:
            query = db_execute(self.dbpath, self.insert, value_fill)

        # Check that query was executed successfully
        if query.error is not None:
            self.errorlog(
                f"failed to upsert new data: {query.error}")
            return False

        # Life is good, all seems well
        self.infolog(
            "upsert successful")
        return True

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

    def infolog(self, msg: str) -> None:
        """Write a message to the log, prefixing it with the module name."""
        self.logger.info(f"{YELLOW_B}{self.name} {GREEN}{msg}{RESET}")

    def warnlog(self, msg: str) -> None:
        """Write a message to the log, prefixing it with the module name."""
        self.logger.info(f"{YELLOW_B}{self.name} {RED}{msg}{RESET}")

    def errorlog(self, msg: str) -> None:
        """Write a message to the log, prefixing it with the module name."""
        self.logger.info(f"{YELLOW_B}{self.name} {MAGENTA}{msg}{RESET}")
