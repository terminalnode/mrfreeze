"""
Mute channels stores information about which channels servers use for mutes.

Table structure:
mute_channels       channel*   INTEGER      Channel ID
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


class MuteChannels:
    """Class for handling the mute_channels table."""

    def __init__(self, dbpath: str) -> None:
        self.dbpath = dbpath
        self.module_name = "Mute channels table"
        self.table_name = "mute_channels"
        self.mute_channels: Optional[Dict[int, int]] = None

        self.table = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            channel     INTEGER NOT NULL,
            server      INTEGER NOT NULL,
            CONSTRAINT server_mute_channel PRIMARY KEY (channel, server)
        );"""

    def initialize(self) -> None:
        """Set up the mute channels table."""
        db_create(self.dbpath, self.module_name, self.table)
        self.mute_channels_from_db()

    def set_mute_channel(self, channel: TextChannel) -> bool:
        """Set the mute channel for a given server using the channel object."""
        return self.upsert(channel.guild, channel.id)

    def set_mute_channel_by_id(self, server: Guild, channel_id: int) -> bool:
        """Set the mute channel for a given server using the channel id."""
        return self.upsert(server, channel_id)

    def upsert(self, server: Guild, value: int) -> bool:
        """Insert or update the value for `server.id` with `value`."""
        sql = f"""INSERT INTO {self.table_name} (server, channel) VALUES (?, ?)
              ON CONFLICT(server) DO UPDATE SET channel = ?;"""
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

    def get_mute_channel(self, server: Guild) -> Optional[int]:
        """Retrieve the mute channel for a given server."""
        # Check that current mutes has been fetched.
        # If not refetch it.
        if self.mute_channels is None:
            self.mute_channels_from_db()

        # Check that it was indeed fetched, otherwise
        # return None as default.
        if self.mute_channels is None:
            return None

        # Check if the requested server has an entry,
        # otherwise return None as default.
        if server.id not in self.mute_channels:
            return None

        # Finally, return the actual value from the dictionary.
        return self.mute_channels[server.id]

    def update_dictionary(self, key: int, value: int) -> bool:
        """Try to update the dictionary with the mute channels."""
        if self.mute_channels is None:
            self.mute_channels_from_db()

        if self.mute_channels is None:
            return False
        else:
            self.mute_channels[key] = value
            return True

    def mute_channels_from_db(self) -> None:
        """
        Load current mute channel values from database.

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

            self.mute_channels = new_dict
            success_print(self.module_name, "successfully fetched mute channels")
        else:
            failure_print(self.module_name, f"failed to fetch mute channels: {query.error}")
            self.mute_channels = None
