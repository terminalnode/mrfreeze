"""Inkbot channels stores information about which channels servers use for the inkcyclopedia."""

import logging

from mrfreeze.database.tables.abc_table_dict import ABCTableDict


class InkcyclopediaChannels(ABCTableDict[int, int]):
    """Class for handling the mute_channels table."""

    def __init__(self, dbpath: str, logger: logging.Logger) -> None:
        self.dbpath = dbpath
        self.name = "inkcyclopedia channels"
        self.table_name = "inkcyclopedia_channels"
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
            channel     INTEGER NOT NULL
        );"""
