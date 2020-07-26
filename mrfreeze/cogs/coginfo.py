"""An object for easily passing information that all cogs should possess."""

from logging import Logger
from typing import Any
from typing import Dict
from typing import Optional

from mrfreeze.bot import MrFreeze


class InsufficientCogInfo(Exception):
    """An exception raised when CogInfo doesn't contain the right information."""


class CogInfo:
    """An object for easily passing information that all cogs should possess."""

    cog: Any
    logger: Optional[Logger]
    bot: Optional[MrFreeze]
    mdbname: Optional[str]
    regions: Optional[Dict[int, Dict[str, Optional[int]]]]
    default_mute_interval: Optional[int]

    def __init__(self, cog: Any) -> None:
        self.cog = cog
        self.set_attribute("logger")
        self.set_attribute("bot")
        self.set_attribute("mdbname")
        self.set_attribute("regions")
        self.set_attribute("default_mute_interval")

    def set_attribute(self, name: str) -> None:
        """Check if the cog has the given attribute and return it."""
        if hasattr(self.cog, name):
            setattr(self, name, getattr(self.cog, name))
        else:
            setattr(self, name, None)

    def has_all_attributes(self, *attrs: str) -> bool:
        """Check if CogInfo has all requested attributes."""
        return any([ hasattr(self, name) for name in attrs ])
