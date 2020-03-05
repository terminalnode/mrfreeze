"""
Store information about which roles servers use for mute.

Table structure:
mute_roles          server*     INTEGER     Server ID
                    role        INTEGER     Role ID
"""

from ..abc_server_settings import ABCServerSetting


class MuteRoles(ABCServerSetting):
    """Class for handling the mute_roles table."""

    def __init__(self, dbpath: str) -> None:
        self.dbpath = dbpath
        self.name = "Mute roles table"
        self.table_name = "mute_roles"
        self.dict = None

        # SQL commands
        self.select_all = f"SELECT server, role FROM {self.table_name}"

        self.insert = f"""
        INSERT INTO {self.table_name} (server, role) VALUES (?, ?)
            ON CONFLICT(server) DO UPDATE SET role = ?
        ;"""

        self.table = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            server      INTEGER NOT NULL PRIMARY KEY,
            role        INTEGER NOT NULL
        );"""
