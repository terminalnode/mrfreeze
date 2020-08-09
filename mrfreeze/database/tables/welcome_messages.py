"""Trash channels stores information about which welcome messages servers use."""

import logging
from typing import Optional

from mrfreeze.database.tables.abc_table_dict import ABCTableDict


class WelcomeMessages(ABCTableDict[int, Optional[str]]):
    """Class for handling the welcome_messages table."""

    def __init__(self, dbpath: str, logger: logging.Logger) -> None:
        self.dbpath = dbpath
        self.name = "welcome messages"
        self.table_name = "welcome_messages"
        self.dict = None
        self.logger = logger
        self.primary_keys = ("server",)
        self.secondary_keys = ("template",)

        # SQL commands
        self.select_all = f"SELECT server, template FROM {self.table_name}"

        self.insert = f"""
        INSERT INTO {self.table_name}
            (server, template) VALUES (?, ?)
        ON CONFLICT(server) DO UPDATE SET template = ?;
        """

        self.table = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            server      INTEGER NOT NULL PRIMARY KEY,
            template    TEXT
        );"""
