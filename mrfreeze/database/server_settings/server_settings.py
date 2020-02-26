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
from .trash_channels import TrashChannels
from .mute_channels import MuteChannels
from .mute_roles import MuteRoles

class ServerSettings():
    def __init__(self, dbpath):
        self.dbpath = dbpath

        # Initiate all the submodules
        self.trash_channels = TrashChannels(self)
        self.mute_channels  = MuteChannels(self)
        self.mute_roles     = MuteRoles(self)
        self.freeze_mutes   = FreezeMutes(self)

        # Link methods from subclasses
        self.toggle_freeze_mute     = self.freeze_mutes.toggle_freeze_mute
        self.freeze_mutes_from_db   = self.freeze_mutes.freeze_mutes_from_db

    def setup_tables(self):
        """Creates the database and tables necessary for the server settings module."""
        self.freeze_mutes.setup_table()
        self.trash_channels.setup_table()
        self.mute_channels.setup_table()
        self.mute_roles.setup_table()
