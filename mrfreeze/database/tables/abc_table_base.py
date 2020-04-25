"""Abstract base class for settings."""

import logging
import sqlite3
from abc import ABCMeta
from abc import abstractmethod
from typing import Any

from mrfreeze.colors import GREEN, MAGENTA, RED, RESET, YELLOW_B

from ..helpers import db_connect


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
    # dict: Optional[Dict[Any, Any]]

    # SQL commands
    select_all: str
    insert: str
    table: str

    # Functions
    @abstractmethod
    def upsert(self, key: Any, value: Any) -> bool:
        """Insert or update something into the database."""
        pass

    @abstractmethod
    def load_from_db(self) -> None:
        """Load all data from the database into memory."""
        pass

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
