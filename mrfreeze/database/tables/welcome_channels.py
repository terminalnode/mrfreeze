"""Mute channels stores information about which channels servers use welcome messages."""

import logging
from typing import Optional

from mrfreeze.database.tables.abc_table_dict import ABCTableDict


class WelcomeChannels(ABCTableDict[int, Optional[int]]):
    """Class for handling the welcome_channels table."""

    def __init__(self, dbpath: str, logger: logging.Logger) -> None:
        self.dbpath = dbpath
        self.name = "welcome channels"
        self.table_name = "welcome_channels"
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
