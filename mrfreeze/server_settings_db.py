"""
Module for writing and reading server settings from the server settings database.

The previous server settings will eventually all be converter to
use the server settings database, probably.

For now this keeps track of:
    Mute channels
    Mute roles
    Trash channels
"""
from enum import Enum
from enum import auto

from mrfreeze import dbfunctions
from mrfreeze.colors import CYAN, CYAN_B, GREEN, GREEN_B, RED, RED_B, YELLOW, RESET

class Tables(Enum):
    SERVER_SETTINGS = auto()
    TRASH_CHANNELS  = auto()
    MUTE_CHANNELS   = auto()
    MUTE_ROLES      = auto()
    FREEZE_MUTES    = auto()

class ServerSettings():
    def __init__(self, bot):
        self.bot = bot

        # Database variables
        self.database = "server_settings"
        self.tables = {
            Tables.TRASH_CHANNELS:  "trash_channels",
            Tables.MUTE_CHANNELS:   "mute_channels",
            Tables.MUTE_ROLES:      "mute_roles",
            Tables.FREEZE_MUTES:    "freeze_mute"
        }

        # This is super long and therefor at the bottom of the class
        self.setup_tables()

        # Load all the server settings into memory
        self.freeze_mutes = self.freeze_mutes_from_db()

    def freeze_mutes_from_db(self):
        error = None

        with dbfunctions.db_connect(self.bot, self.database) as conn:
            c = conn.cursor()
            sql = f"SELECT server, muted FROM {self.tables[Tables.FREEZE_MUTES]}"

            try:
                pass
                c.execute(sql, tuple())
            except Exception as e:
                error = e

        if error is None:
            output = dict()
            for entry in c.fetchall():
                output[entry[0]] = bool(entry[1])

            self.success_printer("successfully fetched freeze mutes")
            return output
        else:
            self.failure_printer("failed to fetch freeze mutes")
            return None

    def success_printer(self, message):
        print(f"{self.bot.current_time()} {GREEN_B}Server settings DB:{CYAN} {message}{RESET}")

    def failure_printer(self, message):
        print(f"{self.bot.current_time()} {RED_B}Region DB:{CYAN} {message}{RESET}")

    def setup_tables(self):
        """Creates the database and tables necessary for the server settings module."""
        # Complete list of tables and their rows in the server settings database.
        # Primary key(s) is marked with an asterisk (*).
        # Mandatory but not primary keys are marked with a pling (!).
        # TABLE                 ROWS       TYPE     FUNCTION
        # self.trash_channels   channel*   INTEGER  Channel ID
        #                       server*    INTEGER  Server ID
        #
        # self.mute_channels    channel*   INTEGER  Channel ID
        #                       server*    INTEGER  Server ID
        #
        # self.mute_roles       role*      INTEGER  Channel ID
        #                       server*    INTEGER  Server ID
        # self.freeze_mute      server*    INTEGER  Server ID
        #                       muted      BOOLEAN  Is muted?
        trash_chan_tbl = f"""
        CREATE TABLE IF NOT EXISTS {self.tables[Tables.TRASH_CHANNELS]} (
            channel     INTEGER NOT NULL,
            server      INTEGER NOT NULL,
            CONSTRAINT server_trash_channel PRIMARY KEY (channel, server)
        );"""

        mute_chan_tbl = f"""
        CREATE TABLE IF NOT EXISTS {self.tables[Tables.MUTE_CHANNELS]} (
            channel     INTEGER NOT NULL,
            server      INTEGER NOT NULL,
            CONSTRAINT server_mute_channel PRIMARY KEY (channel, server)
        );"""

        mute_role_tbl = f"""
        CREATE TABLE IF NOT EXISTS {self.tables[Tables.MUTE_ROLES]} (
            role        INTEGER NOT NULL,
            server      INTEGER NOT NULL,
            CONSTRAINT server_mute_role PRIMARY KEY (role, server)
        );"""

        freeze_mute_tbl = f"""
        CREATE TABLE IF NOT EXISTS {self.tables[Tables.FREEZE_MUTES]} (
            server      INTEGER PRIMARY KEY NOT NULL,
            muted       BOOLEAN NOT NULL
        );"""

        dbfunctions.db_create(self.bot, self.database, trash_chan_tbl,  comment="trash channels table")
        dbfunctions.db_create(self.bot, self.database, mute_chan_tbl,   comment="mute channels table")
        dbfunctions.db_create(self.bot, self.database, mute_role_tbl,   comment="mute roles table")
        dbfunctions.db_create(self.bot, self.database, freeze_mute_tbl, comment="freeze mute table")
