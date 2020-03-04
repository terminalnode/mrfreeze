"""
Trash channels stores information about which channels servers use for trash.

Table structure:
trash_channels      channel*   INTEGER      Channel ID
                    server*    INTEGER      Server ID
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
        self.module_name = "Trash channels table"
        self.table_name = "trash_channels"
        self.trash_channels: Optional[Dict[int, int]] = None

        self.table = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            channel     INTEGER NOT NULL,
            server      INTEGER NOT NULL,
            CONSTRAINT server_trash_channel PRIMARY KEY (channel, server)
        );"""

    def initialize(self) -> None:
        """Set up the trash channels table."""
        db_create(self.dbpath, self.module_name, self.table)

    def set_trash_channel(self, channel: TextChannel) -> bool:
        """Set the trash channel for a given server using the channel object."""
        return self.upsert(channel.guild, channel.id)

    def set_trash_channel_by_id(self, server: Guild, channel_id: int) -> bool:
        """Set the trash channel for a given server using the channel id."""
        return self.upsert(server, channel_id)

    def upsert(self, server: Guild, value: int) -> bool:
        """Insert or update the value for `server.id` with `value`."""
        sql = f"""INSERT INTO {self.table_name} (server, channel) VALUES (?, ?)
              ON CONFLICT(server, channel) DO UPDATE SET channel = ?;"""
        query = db_execute(self.dbpath, sql, (server.id, value, value))

        if query.error is not None:
            failure_print(
                self.module_name,
                f"failed to set {server.name} to {value}\n{query.error}")
            return False

        elif not self.update_dictionary(server.id, value):
            failure_print(
                self.module_name,
                f"failed to update dictionary for {server.name} to {value}\n{query.error}")
            return False

        else:
            success_print(
                self.module_name,
                f"successfully set {server.name} to {value}")
            return True

    def get_trash_channel(self, server: Guild) -> Optional[int]:
        """Retrieve the trash channel for a given server."""
        # Check that current mutes has been fetched.
        # If not refetch it.
        if self.trash_channels is None:
            self.trash_channels_from_db()

        # Check that it was indeed fetched, otherwise
        # return None as default.
        if self.trash_channels is None:
            return None

        # Check if the requested server has an entry,
        # otherwise return None as default.
        if server.id not in self.trash_channels:
            return None

        # Finally, return the actual value from the dictionary.
        return self.trash_channels[server.id]

    def update_dictionary(self, key: int, value: int) -> bool:
        """Try to update the dictionary with the trash channels."""
        if self.trash_channels is None:
            self.trash_channels_from_db()

        if self.trash_channels is None:
            return False
        else:
            self.trash_channels[key] = value
            return True

    def trash_channels_from_db(self) -> None:
        """
        Load current trash channel values from database.

        The values are then stored in a dictionary for quick access.
        Whenever the value is changed, the value in the dictionary and
        the database are updated simultaneously through the upsert method.
        """
        query = db_execute(
            self.dbpath,
            f"SELECT server, channel FROM {self.table_name}",
            tuple())

        if not query.error:
            new_dict = dict()
            for entry in query.output:
                new_dict[entry[0]] = entry[1]

            self.trash_channels = new_dict
            success_print(self.module_name, "successfully fetched trash channels")
        else:
            failure_print(self.module_name, f"failed to fetch trash channels: {query.error}")
            self.trash_channels = None
