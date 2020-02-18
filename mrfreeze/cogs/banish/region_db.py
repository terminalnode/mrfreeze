from typing import List

from discord import Guild
from discord import Member

from mrfreeze.bot import MrFreeze
from mrfreeze.dbfunctions import db_connect
from mrfreeze.colors import CYAN, CYAN_B, GREEN, GREEN_B, RED, RED_B, YELLOW, RESET

# Complete list of tables and their rows in this database.
# (These are created via the banish cog)
#
# Primary key(s) is marked with an asterisk (*).
# Mandatory but not primary keys are marked with a pling (!).
# TABLE                 ROWS       TYPE     FUNCTION
# self.region_table     role*      integer  Role ID
#                       server*    integer  Server ID
#                       triggers!  string   String of keywords for region
# self.blacklist_table  uid*       integer  User ID
#                       sid*       integer  Server ID

def add_blacklist(bot: MrFreeze, dbfile: str, dbtable: str, member: Member) -> bool:
    """
    Add a member to the region blacklist.

    A member who is on the blacklist is not allowed to change their
    region via commands, but they may still use it for Antarctica.
    """
    server = member.guild.id
    servername = member.guild.name
    error = None

    with db_connect(bot, dbfile) as conn:
        c = conn.cursor()
        sql = (f"INSERT INTO {dbtable} (uid, sid) VALUES (?,?)")

        try:
            c.execute(sql, (member.id, server))
        except Exception as e:
            error = e

    if error == None:
        print(f"{bot.current_time()} {GREEN_B}Region DB:{CYAN} added user to blacklist: " +
              f"{CYAN_B}{member} @ {servername}{CYAN}.{RESET}")
        return True
    else:
        print(error)
        return False

def fetch_blacklist(bot: MrFreeze, dbfile: str, dbtable: str, server: Guild) -> List[int]:
    """
    Get a list of all members who are blacklisted on a given server.

    Fetch all the users blacklisted in a given server and return them as a list.
    """
    error = None

    with bot.db_connect(bot, dbfile) as conn:
        c = conn.cursor()
        sql = (f"SELECT uid FROM {dbtable} WHERE sid = ?")

        try:
            c.execute(sql, (server.id,))
        except Exception as e:
            error = e

        if error == None:
            print(f"{bot.current_time()} {GREEN_B}Region DB:{CYAN} fetched blacklist for server: " +
                  f"{CYAN_B}{server.name}{CYAN}.{RESET}")
            return c.fetchall()
        else:
            print(error)
            return list()
