import discord

from discord import Member
from datetime import datetime

from mrfreeze.bot import MrFreeze
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

def add_blacklist(bot: MrFreeze, dbfile: str, dbname: str, member: Member):
    """
    Add a member to the region blacklist.

    A member who is on the blacklist is not allowed to change their
    region via commands, but they may still use it for Antarctica.
    """
    # TODO add some fancy error shenanigans
    server = member.guild.id
    servername = member.guild.name
    error = None

    with bot.db_connect(bot, dbfile) as conn:
        c = conn.cursor()
        sql = (f"INSERT INTO {dbname} (uid, sid) VALUES(?,?)")

        try:
            c.execute(sql, (member.id, server))
        except Exception as e:
            error = e

    if error == None:
        print(f"{bot.current_time()} {GREEN_B}Region DB:{CYAN} added user to blacklist: " +
              f"{CYAN_B}{member} @ {servername}{CYAN}.{RESET}")
        return True
    else:
        return False
