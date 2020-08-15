"""Mute channels stores information about which channels servers use for leave messages."""

import logging
from typing import Optional

from mrfreeze.database.tables.abc_table_dict import ABCTableDict


class LeaveChannels(ABCTableDict[int, Optional[int]]):
    """Class for handling the leave_channels table."""

    def __init__(self, dbpath: str, logger: logging.Logger) -> None:
        self.dbpath = dbpath
        self.name = "leave channels"
        self.table_name = "leave_channels"
        self.dict = None
        self.logger = logger
        self.primary_keys = ("server",)
        self.secondary_keys = ("channel",)

        # SQL commands
        self.select_all = f"SELECT server, channel FROM {self.table_name}"

        self.insert = f"""
        INSERT INTO {self.table_name}
            (server, channel) VALUES (?, ?)
        ON CONFLICT(server) DO UPDATE SET channel = ?;
        """

        self.table = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            server      INTEGER NOT NULL PRIMARY KEY,
            channel     INTEGER
        );"""
