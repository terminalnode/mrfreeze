"""
Store information about which roles servers use for mute.

Table structure:
mute_roles          role*      INTEGER      Channel ID
                    server*    INTEGER      Server ID
"""

from ..helpers import db_create, db_connect, db_time, failure_print, success_print

class MuteRoles:
    def __init__(self, parent):
        self.parent = parent
        self.module_name = "Mute roles table"
        self.table_name = "mute_roles"
        self.table = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            role        INTEGER NOT NULL,
            server      INTEGER NOT NULL,
            CONSTRAINT server_mute_role PRIMARY KEY (role, server)
        );"""

    def initialize(self):
        """Setup the mute_roles table."""
        db_create(self.parent.dbpath, self.module_name, self.table)
