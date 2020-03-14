"""Trash channels stores information about which channels servers use for trash."""

from .abc_table import ABCTable


class TrashChannels(ABCTable):
    """Class for handling the trash_channels table."""

    def __init__(self, dbpath: str) -> None:
        self.dbpath = dbpath
        self.name = "trash channels"
        self.table_name = "trash_channels"
        self.dict = None

        # SQL commands
        self.select_all = f"SELECT server, channel FROM {self.table_name}"

        self.insert = f"""
        INSERT INTO {self.table_name} (server, channel) VALUES (?, ?)
            ON CONFLICT(server) DO UPDATE SET channel = ?
        ;"""

        self.table = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            server      INTEGER NOT NULL PRIMARY KEY,
            channel     INTEGER NOT NULL
        );"""
