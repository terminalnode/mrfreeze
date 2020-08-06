"""Mute interval stores information about how often to check for users due for unmute."""

import logging
from typing import Optional

from mrfreeze.database.tables.abc_table_dict import ABCTableDict


class MuteInterval(ABCTableDict[int, Optional[int]]):
    """
    Class for handling the mute_intervals table.

    This value is used to determine how often to check for users due for unmute.
    """

    def __init__(self, dbpath: str, logger: logging.Logger) -> None:
        self.dbpath = dbpath
        self.name = "mute intervals"
        self.table_name = "mute_intervals"
        self.dict = None
        self.logger = logger
        self.primary_keys = ("server",)
        self.secondary_keys = ("minutes",)

        # SQL commands
        self.select_all = f"SELECT server, minutes FROM {self.table_name}"

        self.insert = f"""
        INSERT INTO {self.table_name}
            (server, minutes) VALUES (?, ?)
        ON CONFLICT(server) DO UPDATE SET minutes = ?;
        """

        self.table = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            server      INTEGER NOT NULL PRIMARY KEY,
            minutes     INTEGER
        );"""
