"""
Module for writing and reading server settings from the server settings database.

The previous server settings will eventually all be converter to
use the server settings database, probably.

Complete list of server settings module tables.
TABLE               ROWS       TYPE         FUNCTION
trash_channels      channel*   INTEGER      Channel ID
                    server*    INTEGER      Server ID

mute_channels       channel*   INTEGER      Channel ID
                    server*    INTEGER      Server ID

mute_roles          role*      INTEGER      Channel ID
                    server*    INTEGER      Server ID

freeze_mutes        server*    INTEGER      Server ID
                    muted      BOOLEAN      Is muted?
"""

from functools import partial
from typing import List
from typing import Optional
from typing import Union

from discord import Guild
from discord import Role
from discord import TextChannel

from .freeze_mutes import FreezeMutes
from .mute_channels import MuteChannels
from .mute_roles import MuteRoles
from .trash_channels import TrashChannels
from ..abc_server_settings import ABCServerSetting
from ..helpers import db_create
from ..helpers import db_execute
from ..helpers import failure_print
from ..helpers import success_print


class ServerSettings():
    """Class for handling all tables relating to server settings."""

    def __init__(self, dbpath: str) -> None:
        self.dbpath = dbpath

        # Link methods from MuteChannels
        self.mute_channels  = MuteChannels(self.dbpath)
        self.get_mute_channel       = partial(self.get, module=self.mute_channels)
        self.set_mute_channel       = partial(self.set, module=self.mute_channels)
        self.set_mute_channel_by_id = partial(self.set_by_id, module=self.mute_channels)

        # Link methods from MuteRoles
        self.mute_roles     = MuteRoles(self.dbpath)
        self.get_mute_role       = partial(self.get, module=self.mute_roles)
        self.set_mute_role       = partial(self.set, module=self.mute_roles)
        self.set_mute_role_by_id = partial(self.set_by_id, module=self.mute_roles)

        # Link methods from TrashChannels
        self.trash_channels = TrashChannels(self.dbpath)
        self.get_trash_channel       = partial(self.get, module=self.trash_channels)
        self.set_trash_channel       = partial(self.set, module=self.trash_channels)
        self.set_trash_channel_by_id = partial(self.set_by_id, module=self.trash_channels)

        # Link methods from FreezeMutes
        self.freeze_mutes   = FreezeMutes(self.dbpath)
        self.is_freeze_muted    = partial(self.get, module=self.freeze_mutes)
        self.toggle_freeze_mute = self.freeze_mutes.toggle

        self.all_modules: List[ABCServerSetting] = [
            self.mute_channels,  self.mute_roles,
            self.trash_channels, self.freeze_mutes
        ]

    def initialize(self) -> None:
        """Set up the database and tables necessary for the server settings module."""
        for module in self.all_modules:
            self.create_table(module)

        for module in self.all_modules:
            self.load_from_db(module)

    def create_table(self, module: ABCServerSetting) -> None:
        """Create the table for a given module."""
        db_create(self.dbpath, module.name, module.table)

    def load_from_db(self, module: ABCServerSetting) -> None:
        """
        Load the values of a given modules from database into memory.

        Each module has a dictionary called self.dict into which the values
        are all loaded. This function generalises this process so it doesn't
        have to be implemented into all the cogs individually.
        """
        query = db_execute(self.dbpath, module.select_all, tuple())

        if query.error is None:
            new_dict = dict()
            for entry in query.output:
                new_dict[entry[0]] = entry[1]

            module.dict = new_dict
            success_print(module.name, "successfully fetched mute roles")
        else:
            failure_print(module.name, f"failed to fetch mute roles: {query.error}")
            module.dict = None

    def get(self, server: Guild, module: ABCServerSetting) -> Optional[int]:
        """Get the value from a given module for a given server."""
        # Check that values are loaded, if not try again.
        if module.dict is None:
            self.load_from_db(module)

        # Check that they loaded properly, otherwise return None.
        if module.dict is None:
            return None

        # Check if requested server has an entry, otherwise return None.
        if server.id not in module.dict:
            return None

        # Finally, return the actual value from the dictionary.
        return module.dict[server.id]

    def update_dictionary(self,
                          module: ABCServerSetting,
                          key: int,
                          value: Union[int, bool]
                          ) -> bool:
        """Update the dictionary for a given module."""
        if module.dict is None:
            self.load_from_db(module)

        if module.dict is None:
            return False
        else:
            module.dict[key] = value
            return True

    def set(self, object: Union[TextChannel, Role], module: ABCServerSetting) -> bool:
        """Set the value using a TextChannel or Role object."""
        return self.upsert(object.guild, object.id, module)

    def set_by_id(self, server: Guild, value: Union[bool, int], module: ABCServerSetting) -> bool:
        """Set the value using a Guild object and a value."""
        return self.upsert(server, value, module)

    def upsert(self, server: Guild, value: Union[int, bool], module: ABCServerSetting) -> bool:
        """Insert or update the value for `server.id` with `value`."""
        query = db_execute(self.dbpath, module.insert, (server.id, value, value))

        if query.error is not None:
            failure_print(
                module.name,
                f"failed to set {server.name} to {value}\n{query.error}")
            return False
        elif not self.update_dictionary(module, server.id, value):
            failure_print(
                module.name,
                f"failed to update dictionary for {server.name} to {value}\n{query.error}")
            return False
        else:
            success_print(
                module.name,
                f"successfully set {server.name} to {value}")
            return True
