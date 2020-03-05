"""Abstract base class for all of the server settings."""

from abc import ABCMeta
from typing import Dict
from typing import Optional
from typing import Union


class ABCServerSetting(metaclass=ABCMeta):
    """
    Abstract base class for Server Settings.

    This class defines a number of properties that every server settings submodule
    needs to be able to interface properly with the main ServerSettings class.
    """

    # General properties
    name: str
    table_name: str
    dict: Optional[Dict[int, Union[bool, int]]]

    # SQL commands
    select_all: str
    insert: str
    table: str
