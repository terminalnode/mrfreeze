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

        self.current_mutes = None

    def initialize(self):
        """Setup the freeze mutes table, then fetch mutes."""
        db_create(self.parent.dbpath, self.module_name, self.table)
        self.freeze_mutes_from_db()

    def is_freeze_muted(self, server):
        """Check freeze mute value for a given server."""
        # Check that current mutes has been fetched.
        # If not refetch it.
        if self.current_mutes is None:
            self.freeze_mutes_from_db()

        # Check that it was indeed fetched, otherwise
        # return False as default.
        if self.current_mutes is None:
            return False

        # Check if the requested server has an entry,
        # otherwise return False as default.
        if server.id not in self.current_mutes:
            return False

        # Finally, return the actual value from the dictionary.
        return self.current_mutes[server.id]


    def toggle_freeze_mute(self, server):
        """
        Toggle the freeze mute value for the specified server.

        If the value is unset, set to true.
        If the value is false, set to true.
        If the value is true, set to false.

        Return the new value.
        """
        name = server.name
        current_value = self.is_freeze_muted(server)
        new_value = not current_value

        return self.upsert(server, new_value)


    def upsert(self, server, value):
        """Insert or replace the value for `server` with `value`."""

        error = None
        sql = f"""INSERT INTO {self.table_name} (server, muted) VALUES (?, ?)
              ON CONFLICT(server) DO UPDATE SET muted = ?;"""

        with db_connect(self.parent.dbpath) as conn:
            c = conn.cursor()

            try:
                c.execute(sql, (server.id, value, value))
            except Exception as e:
                error = e

        if error is None:
            self.current_mutes[server.id] = value
            success_print(
                self.module_name,
                f"successfully set {server.name} to {value}")
            return True
        else:
            failure_print(
                self.module_name,
                f"failed to set {server.name} to {value}\n{error}")
            return False


    def freeze_mutes_from_db(self):
        """
        Load current freeze mute values from database.

        The values are then stored in a dictionary for quick access.
        Whenever the value is changed, the value in the dictionary and
        the database are updated simultaneously through the
        toggle_freeze_mute method.
        """
        error = None
        sql = f"SELECT server, muted FROM {self.table_name}"

        with db_connect(self.parent.dbpath) as conn:
            c = conn.cursor()

            try:
                c.execute(sql, tuple())
            except Exception as e:
                error = e

        if error is None:
            output = dict()
            for entry in c.fetchall():
                output[entry[0]] = bool(entry[1])

            success_print(self.module_name, "successfully fetched mutes")
            self.current_mutes = output
        else:
            failure_print(self.module_name, f"failed to fetch mutes: {error}")
            self.current_mutes = None
