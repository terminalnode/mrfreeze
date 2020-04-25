"""Abstract base class for data best stored in lists."""

import logging
from typing import Any
from typing import List
from typing import Optional

from .abc_table_base import ABCTableBase


class ABCTableList(ABCTableBase):
    """
    Abstract base class for table whose data is best stored in lists.

    This class defines a number of properties and methods common to all
    such tables, making them easier to work with.
    """

    # General properties
    name: str
    table_name: str
    dbpath: str
    logger: logging.Logger
    entries: Optional[List[Any]]

    # SQL commands
    select_all: str
    insert: str
    table: str

    # Placeholder to make sure the module type checks.
    def upsert(self, key: Any, value: Any) -> bool:
        """Insert or update something into the database."""
        pass

    # Placeholder to make sure the module type checks.
    def load_from_db(self) -> None:
        """Load all data from the database into memory."""
        pass
