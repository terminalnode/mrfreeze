"""Mute channels stores information about which channels servers use for mutes."""

import logging
from typing import Optional

from mrfreeze.database.tables.abc_table_dict import ABCTableDict


class SelfMuteTimes(ABCTableDict[int, Optional[int]]):
    """Class for handling the mute_channels table."""

    def __init__(self, dbpath: str, logger: logging.Logger) -> None:
        self.dbpath = dbpath
        self.name = "self mute times"
        self.table_name = "self_mute_times"
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
