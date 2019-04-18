import sqlite3

# A few variables used throughout the module
dbname  = 'Mutes and Banishes'
from internals import var # Colors

def connect_to_db():
    """Creates a connection to the regionbl database."""
    db_file = 'databases/dbfiles/mutes.db'
    conn = sqlite3.connect(db_file)
    return conn

# This function creates the database if it doesn't
# already exists, then closes the connection.
def create():
    """Creates the region blaicklist database with the necessary tables unless it's already created."""
    conn = connect_to_db()

    # Complete list of tables and their rows in this database.
    # Primary key(s) is marked with an asterisk (*).
    # Mandatory but not primary keys are marked with a pling (!).
    # TABLE         ROWS        TYPE        FUNCTION
    # mutes         id*         integer     User ID
    #               server*     integer     Server ID
    #               voluntary!  boolean     If this mute was self-inflicted or not.
    #               until       date        The date when the user should be unbanned.
    #                                       Leave empty if indefinite.
    mutes = """CREATE TABLE IF NOT EXISTS mutes(
        id          integer NOT NULL,
        server      integer NOT NULL,
        voluntary   boolean NOT NULL,
        until       date,
        CONSTRAINT server_user PRIMARY KEY (id, server));"""

    # Now we'll create the database.
    with conn:
        try:
            c = conn.cursor()
            c.execute(mutes)
            print(f'{var.cyan}Database creation successful: {var.green}{dbname}{var.reset}')

        except sqlite3.Error as e:
            print(f'{var.cyan}Database creation failed:     {var.red}{dbname}\n{str(e)}{var.reset}')

# This module needs the following features:
# NAME              FUNCTION
# check()           False if user isn't muted.
#                   True if user is muted indefinitely.
#                   Datetime object is users is muted until a certain time.

# count()           Count all currently muted users. List who they are if requested.
#
# add()             Adds a user to the mute database.
#
# prolong()         Adds extra time to a users mute.

def user_info(user):
    """Returns ((user, server) username) based on a user object."""
    member = user.id
    server = user.guild.id
    name = f'{user.name}#{user.discriminator}'
    return (member, server, name)

def check(user):
    """If a user is muted, return True if it's indefinite and a datetime object if not.
    If a user is not muted, return False."""
    member, server, name = user_info(user)

    with connect_to_db() as conn:
        c = conn.cursor()
        sql = ''' SELECT * FROM mutes WHERE id = ? AND server = ?'''
        c.execute(sql, (member, server))
        fetch = c.fetchall()

    if len(fetch) == 0:
        print(f"{var.cyan}Checked if {var.red}{name} was muted{var.cyan} - they {var.red}were not{var.cyan}.{var.reset}")
        return False
    else:
        print(f"{var.cyan}Checked if {var.green}{name} was muted{var.cyan} - they {var.green}were{var.cyan}.{var.reset}")
        return True # TODO Return True only if there is no time on the mute, otherwise return datetime.
                    # TODO Return information on whether it's a voluntary mute or not.

def count(show=False):
    """Count how many users are currently muted.
    If show is set to True, list all the members if possible."""
    with connect_to_db() as conn:
        c = conn.cursor()

def add(user, voluntary=False, end_date=None):
    """Add a new user to the mutes database."""
    member, server, name = user_info(user)
    error = None
    print(end_date)

    with connect_to_db() as conn:
        c = conn.cursor()
        if end_date != None:
            sql = ''' INSERT INTO mutes(id, server, voluntary, until) VALUES(?,?,?,?)'''
            try:                    c.execute(sql, (member, server, voluntary, end_date))
            except Exception as e:  error = e

        elif end_date == None:
            sql = ''' INSERT INTO mutes(id, server, voluntary) VALUES(?,?,?)'''
            try:                    c.execute(sql, (member, server, voluntary))
            except Exception as e:  error = e

    if error == None:
        print(f"{var.green}{name}{var.cyan} was added to the {var.green}mutes database{var.cyan}.{var.reset}")
        return

    else:
        print(f"{var.cyan}Failed to add {var.red}{name}{var.cyan} to the {var.red}mutes database{var.cyan}:{var.red}\n{error}{var.reset}")
        return


def prolong(user, voluntary=False, end_date=None):
    """Prolong an existing mute in the database.
    A voluntary mute can be made involuntary but not the other way around."""
    member, server, name = user_info(user)
    error = None

    with connect_to_db() as conn:
        c = conn.cursor()


















