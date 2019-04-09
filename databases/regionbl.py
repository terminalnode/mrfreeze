import sqlite3

# A few variables used throughout the module
dbname = 'Region blacklist'
cyan = '\033[0;36m'
green = '\033[32;1m'
red = '\033[31;1m'
reset = '\033[0m'

def connect_to_db():
    """Creates a connection to the regionbl database."""
    db_file = 'databases/dbfiles/regionbl.db'
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
    # blacklists    id*         integer     User ID
    #               server*     integer     Server ID

    blacklists = """CREATE TABLE IF NOT EXISTS region_bl(
        id          integer NOT NULL,
        server      integer NOT NULL,
        CONSTRAINT server_user PRIMARY KEY (id, server));"""

    # Now we'll create the database.
    with conn:
        try:
            c = conn.cursor()
            c.execute(blacklists)
            print(f'{cyan}Database creation successful: {green}{dbname}{reset}')

        except sqlite3.Error as e:
            print(f'{cyan}Database creation failed:     {red}{dbname}\n{e}{reset}')

def user_info(user):
    """Returns ((user, server) username) based on a user object."""
    member = user.id
    server = user.guild.id
    name = f'{user.name}#{user.discriminator}'

    return ((member, server), name)

def check(user):
    """Returns true if the user is blacklisted. False otherwise."""
    member, name = user_info(user)

    with connect_to_db() as conn:
        c = conn.cursor()
        sql = ''' SELECT * FROM region_bl WHERE id = ? AND server = ?'''
        c.execute(sql, member)
        fetch = c.fetchall()

    if len(fetch) == 0:
        return False
    else:
        print(f'{red}{name}{cyan} was caught trying to change their region!{reset}')
        return True

# Split into blacklist(), add() and remove() as we're doing with mutes.

def blacklist(user, add=False, remove=False):
    """Adds and removes users from the blacklist.
    If add is True, add to blacklist.
    If remove is True, remove from blacklist.
    If add == remove, do nothing."""
    member, name = user_info(user)

    with connect_to_db() as conn:
        c = conn.cursor()

        if add and not remove:
            sql = '''INSERT INTO region_bl (id, server)
                VALUES (?,?)'''
        elif remove and not add:
            sql = ''' DELETE FROM region_bl WHERE id = ? AND server = ? '''

        if add != remove:
            try:
                c.execute(sql, member)
                if add:
                    print(f'{green}{name}{cyan} was added to the region blacklist.{reset}')
                    return (True, True)
                elif remove:
                    print(f'{green}{name}{cyan} was removed from the region blacklist.{reset}')
                    return (True, False)
            except sqlite3.Error as e:
                if "UNIQUE constraint" in str(e):
                    print(f'{red}{name}{cyan} is already in the region blacklist.{reset}')
                else:
                    print(f'{cyan}An sqlite3 exception occured when editing {red}{name}{cyan} in the region blacklist:\n{e}{reset}')
                return (False, add)

            except Exception as e:
                print(f'{cyan}A general exception occured when editing {red}{name}{cyan} in the region blacklist:\n{e}{reset}')
                return (False, add)


