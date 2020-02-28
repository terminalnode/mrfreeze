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

from .freeze_mutes import FreezeMutes
from .mute_channels import MuteChannels
from .mute_roles import MuteRoles
from .trash_channels import TrashChannels


class ServerSettings():
    """Class for handling all tables relating to server settings."""

    def __init__(self, dbpath: str) -> None:
        self.dbpath = dbpath

        # Initiate all the submodules
        self.trash_channels = TrashChannels(self)
        self.mute_channels  = MuteChannels(self)
        self.mute_roles     = MuteRoles(self)
        self.freeze_mutes   = FreezeMutes(self)

        # Link methods from MuteChannels
        self.get_mute_channel       = self.mute_channels.get_mute_channel
        self.set_mute_channel       = self.mute_channels.set_mute_channel
        self.set_mute_channel_by_id = self.mute_channels.set_mute_channel_by_id

        # Link methods from FreezeMutes
        self.toggle_freeze_mute = self.freeze_mutes.toggle_freeze_mute
        self.is_freeze_muted    = self.freeze_mutes.is_freeze_muted

    def initialize(self) -> None:
        """Create the database and tables necessary for the server settings module."""
        self.freeze_mutes.initialize()
        self.trash_channels.initialize()
        self.mute_channels.initialize()
        self.mute_roles.initialize()
