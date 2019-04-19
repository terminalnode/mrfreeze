import sqlite3, datetime
from internals import var
dbname  = 'Mutes and Banishes'

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
        CONSTRAINT  server_user PRIMARY KEY (id, server));"""

    # Now we'll create the database.
    with conn:
        try:
            c = conn.cursor()
            c.execute(mutes)
            print(f'{var.cyan}Database creation successful: {var.green}{dbname}{var.reset}')

        except sqlite3.Error as e:
            print(f'{var.cyan}Database creation failed:     {var.red}{dbname}\n{str(e)}{var.reset}')

# This module needs the following features:
# NAME                      FUNCTION
# check(user)               False if user isn't muted.
#                           True if user is muted indefinitely.
#                           Datetime object is users is muted until a certain time.
# parsetime(string or date) Create a datetime from string or a string from datetime.             
# fetch_server(server)      Get a list of all mutes for a server.
# count(server)             Count all currently muted users.
# list_server(server)       Get a list of all mutes in a server and if they are due.
# add()                     Adds a user to the mute database.
# prolong()                 Adds extra time to a users mute.
# remove()                  Removes a user from the mute database.

def parsetime(before):
    timeformat = "%Y-%m-%d %H:%M:%S"

    if isinstance(before, datetime.datetime):
        return datetime.datetime.strftime(before, timeformat)
    elif isinstance(before, str):
        return datetime.datetime.strptime(before, timeformat)
    else:
        return None

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
        return False
    else:
        fetch = fetch[0]
        if len(fetch) < 4: # This means there's no date on the fetch.
            return True
        else:
            return parsetime(fetch[3])

def fetch_server(server):
    """Count how many users are currently muted.
    If show is set to True, list all the members if possible."""
    server = server.id
    with connect_to_db() as conn:
        c = conn.cursor()
        sql = ''' SELECT * FROM mutes WHERE server = ? '''
        c.execute(sql, (server,))
        fetch = c.fetchall()
    return fetch

def list_server(server):
    """List all banishes in a server and if they are due for unbanish."""
    banishes = list()
    current = datetime.datetime.now()

    raw_list = fetch_server(server)
    for banishment in raw_list:
        entry = dict()
        entry['user']       = banishment[0]
        entry['voluntary']  = banishment[2]
        try:
            entry['due'] = bool(parsetime(banishment[3]) < current)
        except:
            entry['due'] = None
        banishes.append(entry)

    return banishes

def count(server):
    """Count how many users are currently muted.
    If show is set to True, list all the members if possible."""
    return len(fetch_server(server))

def add(user, voluntary=False, end_date=None):
    """Add a new user to the mutes database."""
    member, server, name = user_info(user)
    error = None

    with connect_to_db() as conn:
        c = conn.cursor()
        if end_date != None:
            end_date = parsetime(end_date)
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


def remove(user):
    """Removes a user from the mutes database."""
    member, server, name = user_info(user)

    with connect_to_db() as conn:
        c = conn.cursor()
        sql = ''' DELETE FROM mutes WHERE id = ? AND server = ? '''

        try:
            c.execute(sql, (member, server))
            return True

        except Exception as e:
            print(f"Ugh, couldn't remove {name} from mutes db: {e}")
            return False

















