"""Store inks from the inkcyclopedia."""

import logging

from .abc_table_dict import ABCTableDict


class InkcyclopediaInks(ABCTableDict):
    """Class for handling the mute_roles table."""

    def __init__(self, dbpath: str, logger: logging.Logger) -> None:
        self.dbpath = dbpath
        self.name = "inkcyclopedia inks"
        self.table_name = "inkcyclopedia_inks"
        self.dict = None
        self.logger = logger
        self.primary_keys = ("name",)
        self.secondary_keys = ("url", "regex")

        # SQL commands
        self.select_all = f"SELECT name, url, regex FROM {self.table_name}"

        self.insert = f"""
        INSERT INTO {self.table_name}
            (name, url, regex) VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET url = ?, regex = ?;
        """

        self.table = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            name      VARCHAR(63) NOT NULL PRIMARY KEY,
            url       VARCHAR(255) NOT NULL,
            regex     VARCHAR(127)
        );"""
