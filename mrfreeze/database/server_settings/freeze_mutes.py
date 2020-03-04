"""
Freeze mutes stores information about which servers have inactivated Mr Freeze.

Table structure:
freeze_mutes        server*     INTEGER     Server ID
                    muted       BOOLEAN     Is muted?
"""

from typing import Dict
from typing import Optional

from discord import Guild

from ..helpers import db_create
from ..helpers import db_execute
from ..helpers import failure_print
from ..helpers import success_print


class FreezeMutes:
    """Class for handling the freeze_mutes table."""

    def __init__(self, dbpath: str) -> None:
        self.dbpath = dbpath
        self.name = "Freeze Mutes table"
        self.table_name = "freeze_mutes"
        self.dict: Optional[Dict[int, bool]] = None

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

    def initialize(self) -> None:
        """Set up the freeze mutes table, then fetch mutes."""
        db_create(self.dbpath, self.name, self.table)
        self.load_from_db()

    def get(self, server: Guild) -> Optional[bool]:
        """Check freeze mute value for a given server."""
        # Check that current mutes has been fetched.
        # If not refetch it.
        if self.dict is None:
            self.load_from_db()

        # Check that it was indeed fetched, otherwise
        # return False as default.
        if self.dict is None:
            return None

        # Check if the requested server has an entry,
        # otherwise return False as default.
        if server.id not in self.dict:
            return None

        # Finally, return the actual value from the dictionary.
        return self.dict[server.id]

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

    def upsert(self, server: Guild, value: bool) -> bool:
        """Insert or replace the value for `server` with `value`."""
        query = db_execute(self.dbpath, self.insert, (server.id, value, value))

        if query.error is not None:
            failure_print(
                self.name,
                f"failed to set {server.name} to {value}\n{query.error}")
            return False

        elif not self.update_dictionary(server.id, value):
            failure_print(
                self.name,
                f"failed to update dictionary for {server.name} to {value}\n{query.error}")
            return False

        else:
            success_print(
                self.name,
                f"successfully set {server.name} to {value}")
            return True

    def update_dictionary(self, key: int, value: bool) -> bool:
        """Try to update the dictionary with the mute channels."""
        if self.dict is None:
            self.load_from_db()

        if self.dict is None:
            return False
        else:
            self.dict[key] = value
            return True

    def load_from_db(self) -> None:
        """
        Load current freeze mute values from database.

        The values are then stored in a dictionary for quick access.
        Whenever the value is changed, the value in the dictionary and
        the database are updated simultaneously through the
        toggle_freeze_mute method.
        """
        query = db_execute(self.dbpath, self.select_all, tuple())

        if query.error is None:
            new_mutes = dict()
            for entry in query.output:
                new_mutes[entry[0]] = bool(entry[1])

            self.dict = new_mutes
            success_print(self.name, "successfully fetched mutes")
        else:
            self.dict = None
            failure_print(self.name, f"failed to fetch mutes: {query.error}")
