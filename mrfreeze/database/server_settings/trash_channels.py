"""
Trash channels stores information about which channels servers use for trash.

Table structure:
trash_channels      channel*   INTEGER      Channel ID
                    server*    INTEGER      Server ID
"""

from ..helpers import db_create, db_connect, db_time, failure_print, success_print

class TrashChannels:
    def __init__(self, parent):
        self.parent = parent
        self.module_name = "Trash channels table"
        self.table_name = "trash_channels"
        self.table = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            channel     INTEGER NOT NULL,
            server      INTEGER NOT NULL,
            CONSTRAINT server_trash_channel PRIMARY KEY (channel, server)
        );"""

    def setup_table(self):
        """Setup the trash channels table."""
        db_create(self.parent.dbpath, self.module_name, self.table)
