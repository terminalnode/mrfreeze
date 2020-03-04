"""
Trash channels stores information about which channels servers use for trash.

Table structure:
trash_channels      server*     INTEGER     Server ID
                    channel     INTEGER     Channel ID
"""

from typing import Dict
from typing import Optional

from discord import Guild
from discord import TextChannel

from ..helpers import db_create
from ..helpers import db_execute
from ..helpers import failure_print
from ..helpers import success_print


class TrashChannels:
    """Class for handling the trash_channels table."""

    def __init__(self, dbpath: str) -> None:
        self.dbpath = dbpath
        self.name = "Trash channels table"
        self.table_name = "trash_channels"
        self.dict: Optional[Dict[int, int]] = None

        # SQL commands
        self.select_all = f"SELECT server, channel FROM {self.table_name}"

        self.insert = f"""
        INSERT INTO {self.table_name} (server, channel) VALUES (?, ?)
            ON CONFLICT(server) DO UPDATE SET channel = ?
        ;"""

        self.table = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            server      INTEGER NOT NULL PRIMARY KEY,
            channel     INTEGER NOT NULL
        );"""

    def initialize(self) -> None:
        """Set up the trash channels table."""
        db_create(self.dbpath, self.name, self.table)
        self.load_from_db()

    def set(self, channel: TextChannel) -> bool:
        """Set the trash channel for a given server using the channel object."""
        return self.upsert(channel.guild, channel.id)

    def set_by_id(self, server: Guild, channel_id: int) -> bool:
        """Set the trash channel for a given server using the channel id."""
        return self.upsert(server, channel_id)

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
        """Retrieve the trash channel for a given server."""
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
        """Try to update the dictionary with the trash channels."""
        if self.dict is None:
            self.load_from_db()

        if self.dict is None:
            return False
        else:
            self.dict[key] = value
            return True

    def load_from_db(self) -> None:
        """
        Load current trash channel values from database.

        The values are then stored in a dictionary for quick access.
        Whenever the value is changed, the value in the dictionary and
        the database are updated simultaneously through the upsert method.
        """
        query = db_execute(
            self.dbpath,
            self.select_all,
            tuple())

        if not query.error:
            new_dict = dict()
            for entry in query.output:
                new_dict[entry[0]] = entry[1]

            self.dict = new_dict
            success_print(self.name, "successfully fetched trash channels")
        else:
            failure_print(self.name, f"failed to fetch trash channels: {query.error}")
            self.dict = None
