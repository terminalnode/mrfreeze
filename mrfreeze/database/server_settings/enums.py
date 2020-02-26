"""Enums for the server_settings module."""

from enum import Enum
from enum import auto

class Tables(Enum):
    TRASH_CHANNELS  = auto()
    MUTE_CHANNELS   = auto()
    MUTE_ROLES      = auto()
    FREEZE_MUTES    = auto()
