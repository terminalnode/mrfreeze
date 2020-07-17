"""An object for easily passing information that all cogs should possess."""

from logging import Logger
from typing import Any
from typing import Optional

from mrfreeze.bot import MrFreeze


class CogInfo:
    """An object for easily passing information that all cogs should possess."""

    cog: Any
    logger: Optional[Logger]
    bot: Optional[MrFreeze]
    mdbname: Optional[str]

    def __init__(self, cog: Any) -> None:
        self.cog = cog
        self.set_attribute("logger")
        self.set_attribute("bot")
        self.set_attribute("mdbname")

    def set_attribute(self, name: str) -> None:
        """Check if the cog has the given attribute and return it."""
        if hasattr(self.cog, name):
            setattr(self, name, getattr(self.cog, name))
        else:
            setattr(self, name, None)

    def has_all_attributes(self, *attrs: str) -> bool:
        """Check if CogInfo has all requested attributes."""
        return any([ hasattr(self, name) for name in attrs ])
