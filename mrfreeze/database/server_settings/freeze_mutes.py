"""
Freeze mutes stores information about which servers have inactivated Mr Freeze.

Table structure:
freeze_mutes        server*    INTEGER      Server ID
                    muted      BOOLEAN      Is muted?
"""

from ..helpers import db_create, db_connect, db_time, failure_print, success_print

class FreezeMutes:
    def __init__(self, parent):
        self.parent = parent
        self.module_name = "Freeze Mutes table"
        self.table_name = "freeze_mutes"
        self.table = f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
                            server      INTEGER PRIMARY KEY NOT NULL,
                            muted       BOOLEAN NOT NULL);"""

    def setup_table(self):
        """Setup the freeze mutes table."""
        db_create(self.parent.dbpath, self.module_name, self.table)


    def toggle_freeze_mute(self):
        """
        Toggle the freeze mute value for the specified server.

        If the value is unset, set to true.
        If the value is false, set to true.
        If the value is true, set to false.
        """
        pass
        #sid = server.id
        #name = server.name


    def freeze_mutes_from_db(self):
        """
        Load current freeze mute values from database.

        The values are then stored in a dictionary for quick access.
        Whenever the value is changed, the value in the dictionary and
        the database are updated simultaneously through the
        toggle_freeze_mute method.
        """

        error = None

        with db_connect(self.parent.dbpath) as conn:
            c = conn.cursor()
            sql = f"SELECT server, muted FROM {self.table_name}"

            try:
                pass
                c.execute(sql, tuple())
            except Exception as e:
                error = e

        if error is None:
            output = dict()
            for entry in c.fetchall():
                output[entry[0]] = bool(entry[1])

            success_print(self.module_name, "successfully fetched freeze mutes")
            return output
        else:
            failure_print(self.module_name, "failed to fetch freeze mutes")
            return None
