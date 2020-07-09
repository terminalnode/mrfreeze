"""Store information about which roles servers use for mute."""

import logging

from mrfreeze.database.tables.abc_table_dict import ABCTableDict


class MuteRoles(ABCTableDict):
    """Class for handling the mute_roles table."""

    def __init__(self, dbpath: str, logger: logging.Logger) -> None:
        self.dbpath = dbpath
        self.name = "mute roles"
        self.table_name = "mute_roles"
        self.dict = None
        self.logger = logger
        self.primary_keys = ("server",)
        self.secondary_keys = ("role",)

        # SQL commands
        self.select_all = f"SELECT server, role FROM {self.table_name}"

        self.insert = f"""
        INSERT INTO {self.table_name}
            (server, role) VALUES (?, ?)
        ON CONFLICT(server) DO UPDATE SET role = ?;
        """

        self.table = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            server      INTEGER NOT NULL PRIMARY KEY,
            role        INTEGER NOT NULL
        );"""
