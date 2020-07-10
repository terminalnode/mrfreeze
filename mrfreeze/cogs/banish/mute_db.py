"""Module for handling various database interractions with the mute_db."""

from datetime import datetime
from typing import NamedTuple

import discord
from discord import Member

from mrfreeze.lib.colors import CYAN
from mrfreeze.lib.colors import CYAN_B
from mrfreeze.lib.colors import GREEN
from mrfreeze.lib.colors import GREEN_B
from mrfreeze.lib.colors import RED
from mrfreeze.lib.colors import RED_B
from mrfreeze.lib.colors import RESET
from mrfreeze.lib.colors import YELLOW


class BanishTuple(NamedTuple):
    """NamedTuple for holding banish information."""

    member: Member
    voluntary: bool
    until: datetime


# Complete list of tables and their rows in this database.
# (These are created via the banish cog)
#
# Primary key(s) is marked with an asterisk (*).
# Mandatory but not primary keys are marked with a pling (!).
# TABLE         ROWS        TYPE        FUNCTION
# self.mdbname  id*         integer     User ID
#               server*     integer     Server ID
#               voluntary!  boolean     If this mute was self-inflicted or not
#               until       date        The date when the user will be unbanned
#                                       Leave empty if indefinite

async def carry_out_banish(bot, mdbname, member, end_date):
    """
    Add the antarctica role to a user, then add them to the db.

    Return None if successful, Exception otherwise.
    """
    server = member.guild
    roles = member.roles
    mute_role = await bot.get_mute_role(server)
    result = None

    if mute_role not in roles:
        try:
            await member.add_roles(mute_role)
        except Exception as e:
            result = e

    if not isinstance(result, Exception):
        mdb_add(bot, mdbname, member, end_date=end_date)

    return result


async def carry_out_unbanish(bot, mdbname, member):
    """
    Remove the antarctica role from a user, then remove them from the db.

    Return None if successful, Exception otherwise.
    """
    server = member.guild
    roles = member.roles
    mute_role = await bot.get_mute_role(server)
    result = None

    if mute_role in roles:
        try:
            await member.remove_roles(mute_role)
        except Exception as e:
            result = e

    if not isinstance(result, Exception):
        mdb_del(bot, mdbname, member)

    return result


def mdb_add(bot, mdbname, user, voluntary=False, end_date=None, prolong=True):
    """Add a new user to the mutes database."""
    is_member = isinstance(user, discord.Member)
    if not is_member:
        # This should never happen, no point in even logging it.
        raise TypeError(f"Expected discord.Member, got {type(user)}")

    uid = user.id
    server = user.guild.id
    servername = user.guild.name
    name = f"{user.name}#{user.discriminator}"
    error = None
    until = str()     # this string is filled in if called with an end_date
    duration = str()  # this string too

    current_mute = mdb_fetch(bot, mdbname, user)
    is_muted = len(current_mute) != 0
    if is_muted:
        # Always delete existing mutes
        mdb_del(bot, mdbname, user)

    if is_muted and end_date is not None and prolong:
        old_until = current_mute[0].until
        # if current mute is permanent just replace it with a timed one
        if old_until is not None:
            diff = end_date - datetime.now()
            try:
                end_date = old_until + diff
            except OverflowError:
                end_date = datetime.max

    with bot.db_connect(bot, mdbname) as conn:
        c = conn.cursor()
        if end_date is not None:
            # Collect time info in string format for the log
            until = bot.db_time(end_date)
            until = f"\n{GREEN}==> Until: {until} {RESET}"

            duration = end_date - datetime.now()
            duration = bot.parse_timedelta(duration)
            duration = f"{YELLOW}(in {duration}){RESET}"

            # Turn datetime object into string
            end_date = bot.db_time(end_date)

            sql = (f"INSERT INTO {mdbname}(id, server, voluntary, until) " +
                   "VALUES(?,?,?,?)")

            try:
                c.execute(sql, (uid, server, voluntary, end_date))
            except Exception as e:
                error = e

        elif end_date is None:
            sql = (f"INSERT INTO {mdbname}(id, server, voluntary) " +
                   "VALUES(?,?,?)")
            try:
                c.execute(sql, (uid, server, voluntary))
            except Exception as e:
                error = e

    if error == None:
        print(f"{bot.current_time()} {GREEN_B}Mutes DB:{CYAN} added user to DB: " +
                f"{CYAN_B}{name} @ {servername}{CYAN}.{RESET}{until}{duration}")
        return True

    else:
        print(f"{bot.current_time()} {RED_B}Mutes DB:{CYAN} failed adding to DB: " +
                f"{CYAN_B}{name} @ {servername}{CYAN}:" +
                f"\n{RED}==> {error}{RESET}")
        return False


def mdb_del(bot, mdbname, user):
    """Remove a user from the mutes database."""
    is_member = isinstance(user, discord.Member)
    if not is_member:
        # This should never happen, no point in even logging it.
        raise TypeError(f"Expected discord.Member, got {type(user)}")

    uid = user.id
    server = user.guild.id
    servername = user.guild.name
    name = f"{user.name}#{user.discriminator}"

    is_muted = len(mdb_fetch(bot, mdbname, user)) != 0
    if not is_muted:
        print(f"{bot.current_time()} {GREEN_B}Mutes DB:{CYAN} user already not in DB: " +
            f"{CYAN_B}{name} @ {servername}{CYAN}.{RESET}")
        return True

    with bot.db_connect(bot, mdbname) as conn:
        c = conn.cursor()
        sql = f"DELETE FROM {mdbname} WHERE id = ? AND server = ?"

        try:
            c.execute(sql, (uid, server))
            print(f"{bot.current_time()} {GREEN_B}Mutes DB:{CYAN} removed user from DB: " +
                f"{CYAN_B}{name} @ {servername}{CYAN}.{RESET}")
            return True

        except Exception as error:
            print(f"{bot.current_time()} {RED_B}Mutes DB:{CYAN} failed to remove from DB: " +
                f"{CYAN_B}{name} @ {servername}{CYAN}:" +
                f"\n{RED}==> {error}{RESET}")
            return False


def mdb_fetch(bot, mdbname, in_data):
    """
    Return user or server mute information.

    If input is a server, return a list of all users from that server in the database.
    If input is a member, return what we've got on that member.
    """
    is_member = isinstance(in_data, discord.Member)
    is_server = isinstance(in_data, discord.Guild)

    if not is_member and not is_server:
        # This should never happen, no point in even logging it.
        raise TypeError(f"Expected discord.Member or discord.Guild, got {type(in_data)}")

    with bot.db_connect(bot, mdbname) as conn:
        c = conn.cursor()
        fetch_id = in_data.id
        if is_member:
            server = in_data.guild
            sql = f' SELECT * FROM {mdbname} WHERE id = ? AND server = ? '
            c.execute(sql, (fetch_id, server.id))

        elif is_server:
            server = in_data
            sql = f' SELECT * FROM {mdbname} WHERE server = ? '
            c.execute(sql, (fetch_id,))

        output = [
            BanishTuple(
                member = discord.utils.get(server.members, id=int(entry[0])),
                voluntary = bool(entry[2]),
                until = bot.db_time(entry[3])
            )
            for entry in c.fetchall()
        ]

    return output
