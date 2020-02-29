"""
Store information about which roles servers use for mute.

Table structure:
mute_roles          role*      INTEGER      Channel ID
                    server*    INTEGER      Server ID
"""

from ..helpers import db_create
# from ..helpers import db_execute
# from ..helpers import failure_print
# from ..helpers import success_print


class MuteRoles:
    """Class for handling the mute_roles table."""

    def __init__(self, dbpath: str) -> None:
        self.dbpath = dbpath
        self.module_name = "Mute roles table"
        self.table_name = "mute_roles"
        self.table = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            role        INTEGER NOT NULL,
            server      INTEGER NOT NULL,
            CONSTRAINT server_mute_role PRIMARY KEY (role, server)
        );"""

    def initialize(self) -> None:
        """Set up the mute_roles table."""
        db_create(self.dbpath, self.module_name, self.table)
