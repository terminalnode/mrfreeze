"""
Store information about which roles servers use for mute.

Table structure:
mute_roles          server*     INTEGER     Server ID
                    role        INTEGER     Role ID
"""

from typing import Dict
from typing import Optional

from discord import Guild
from discord import Role

from ..helpers import db_create
from ..helpers import db_execute
from ..helpers import failure_print
from ..helpers import success_print


class MuteRoles:
    """Class for handling the mute_roles table."""

    def __init__(self, dbpath: str) -> None:
        self.dbpath = dbpath
        self.name = "Mute roles table"
        self.table_name = "mute_roles"
        self.dict: Optional[Dict[int, int]] = None

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

    def initialize(self) -> None:
        """Set up the mute_roles table."""
        db_create(self.dbpath, self.name, self.table)
        self.load_from_db()

    def set(self, role: Role) -> bool:
        """Set the mute role for a given server using the role object."""
        return self.upsert(role.guild, role.id)

    def set_by_id(self, server: Guild, role_id: int) -> bool:
        """Set the mute role for a given server using the role id."""
        return self.upsert(server, role_id)

    def upsert(self, server: Guild, value: int) -> bool:
        """Insert or update the value for `server.id` with `value`."""
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

    def get(self, server: Guild) -> Optional[int]:
        """Retrieve the mute role for a given server."""
        # Check that current mutes has been fetched.
        # If not refetch it.
        if self.dict is None:
            self.load_from_db()

        # Check that it was indeed fetched, otherwise
        # return None as default.
        if self.dict is None:
            return None

        # Check if the requested server has an entry,
        # otherwise return None as default.
        if server.id not in self.dict:
            return None

        # Finally, return the actual value from the dictionary.
        return self.dict[server.id]

    def update_dictionary(self, key: int, value: int) -> bool:
        """Try to update the dictionary with the mute roles."""
        if self.dict is None:
            self.load_from_db()

        if self.dict is None:
            return False
        else:
            self.dict[key] = value
            return True

    def load_from_db(self) -> None:
        """
        Load current mute role values from database.

        The values are then stored in a dictionary for quick access.
        Whenever the value is changed, the value in the dictionary and
        the database are updated simultaneously through the upsert method.
        """
        query = db_execute(self.dbpath, self.select_all, tuple())

        if not query.error:
            new_dict = dict()
            for entry in query.output:
                new_dict[entry[0]] = entry[1]

            self.dict = new_dict
            success_print(self.name, "successfully fetched mute roles")
        else:
            failure_print(self.name, f"failed to fetch mute roles: {query.error}")
            self.dict = None
