"""Freeze mutes stores information about which servers have inactivated Mr Freeze."""

from discord import Guild

from .abc_table import ABCTable


class FreezeMutes(ABCTable):
    """Class for handling the freeze_mutes table."""

    def __init__(self, dbpath: str) -> None:
        self.dbpath = dbpath
        self.name = "freeze mutes"
        self.table_name = "freeze_mutes"
        self.dict = None

        # SQL commands
        self.select_all = f"SELECT server, muted FROM {self.table_name}"

        self.insert = f"""
        INSERT INTO {self.table_name} (server, muted) VALUES (?, ?)
            ON CONFLICT(server) DO UPDATE SET muted = ?
        ;"""

        self.table = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            server      INTEGER PRIMARY KEY NOT NULL,
            muted       BOOLEAN NOT NULL
        );"""

    def toggle(self, server: Guild) -> bool:
        """
        Toggle the freeze mute value for the specified server.

        If the value is unset, set to true.
        If the value is false, set to true.
        If the value is true, set to false.

        Return the new value.
        """
        new_value = not self.get(server)
        return self.upsert(server, new_value)
