"""
Class for coordinating all the different settings modules.

This class loads all of the different settings sub-modules
and provides a single interface for working with them all.
"""

from typing import List

from .tables.abc_table import ABCTable
from .tables.freeze_mutes import FreezeMutes
from .tables.mute_channels import MuteChannels
from .tables.mute_roles import MuteRoles
from .tables.trash_channels import TrashChannels


class Settings:
    """Settings is a class for coordinating all the various settings modules."""

    def __init__(self) -> None:
        self.dbpath = "settings.db"
        self.tables: List[ABCTable] = list()

        # Initialize the tables
        self.freeze_mutes   = FreezeMutes(self.dbpath)
        self.mute_channels  = MuteChannels(self.dbpath)
        self.mute_roles     = MuteRoles(self.dbpath)
        self.trash_channels = TrashChannels(self.dbpath)

        # Add tables to self.tables
        self.tables.append(self.freeze_mutes)
        self.tables.append(self.mute_channels)
        self.tables.append(self.mute_roles)
        self.tables.append(self.trash_channels)

        # Initialize all the tables
        self.initialize()

        # Link all the methods
        # Freeze Mutes
        self.is_freeze_muted         = self.freeze_mutes.get
        self.toggle_freeze_mute      = self.freeze_mutes.toggle

        # Mute Channels
        self.get_mute_channel        = self.mute_channels.get
        self.set_mute_channel        = self.mute_channels.set
        self.set_mute_channel_by_id  = self.mute_channels.set_by_id

        # Mute Roles
        self.get_mute_role           = self.mute_roles.get
        self.set_mute_role           = self.mute_roles.set
        self.set_mute_role_by_id     = self.mute_roles.set_by_id

        # Trash Channels
        self.get_trash_channel       = self.trash_channels.get
        self.set_trash_channel       = self.trash_channels.set
        self.set_trash_channel_by_id = self.trash_channels.set_by_id

    def initialize(self) -> None:
        """Set up the database and tables necessary for the server settings module."""
        for module in self.tables:
            module.create_table()

        for module in self.tables:
            module.load_from_db()
