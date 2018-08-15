import sqlite3, discord
from sqlite3 import Error

# This file manages the userdb where we keep stuff like rps scores, mutes,
# etc. We also have a register of all channels and users which is constantly
# updated as new information is provided.

# This short function creates the connection to the database.
# It's used in almost every function so it's useful to have.
def connect_to_db():
    db_file = 'databases/user.db'
    conn = sqlite3.connect(db_file)
    return conn

# This function creates the database if it doesn't
# already exists, then closes the connection.
def create():
    conn = connect_to_db()

    # The tables are arranged by the foreign keys they are using.
    # 'servers' is essentially the top table. crt is short for create,
    # tbl is short for table.

    # Server names.
    crt_servers_tbl   = """   CREATE TABLE IF NOT EXISTS servers(
                        id integer PRIMARY KEY,
                        name text NOT NULL
    );"""

    # Channel IDs/Names.
    crt_channels_tbl  = """   CREATE TABLE IF NOT EXISTS channels(
                        id integer PRIMARY KEY,
                        server integer NOT NULL,
                        name text NOT NULL,
                        FOREIGN KEY (server) REFERENCES servers (id)
    );"""

    # List of user IDs/Names.
    crt_users_tbl     = """   CREATE TABLE IF NOT EXISTS users(
                        id integer NOT NULL,
                        server integer NOT NULL,
                        disp_name text NOT NULL,
                        name text NOT NULL,
                        avatar text NOT NULL,
                        discriminator integer NOT NULL,
                        FOREIGN KEY (server) REFERENCES servers (id),
                        CONSTRAINT server_user PRIMARY KEY (id, server)
    );"""

    # Quotes database.
    crt_quotes_tbl    = """  CREATE TABLE IF NOT EXISTS quotes(
                        id integer PRIMARY KEY NOT NULL,
                        quoter integer NOT NULL,
                        quotee integer NOT NULL,
                        server integer NOT NULL,
                        channel integer NOT NULL,
                        date_said text NOT NULL,
                        content text NOT NULL,
                        shortcut text,
                        FOREIGN KEY (quoter) REFERENCES users (id),
                        FOREIGN KEY (quotee) REFERENCES users (id),
                        FOREIGN KEY (server) REFERENCES servers (id),
                        FOREIGN KEY (channel) REFERENCES channels (id)
    );"""

    # Rock, Paper, Scissors stats.
    crt_rps_tbl       = """   CREATE TABLE IF NOT EXISTS rps(
                        id integer PRIMARY KEY NOT NULL,
                        wins integer NOT NULL,
                        losses integer NOT NULL,
                        drawn integer NOT NULL,
                        FOREIGN KEY (id) REFERENCES users (id)
    );"""

    # If a user gets antarctica'd, that's registered here.
    # A user can self-banish, in which case voluntary will be
    # True and they're allowed to unbanish themselves as well.
    crt_mutes_tbl     = """   CREATE TABLE IF NOT EXISTS mutes(
                        user integer NOT NULL,
                        until date NOT NULL,
                        voluntary boolean NOT NULL,
                        FOREIGN KEY (user) REFERENCES users (id)
    );"""

    # Here we'll create all the tables.
    with conn:
        try:
            c = conn.cursor()
            c.execute(crt_servers_tbl)
            c.execute(crt_channels_tbl)
            c.execute(crt_users_tbl)
            c.execute(crt_quotes_tbl)
            c.execute(crt_rps_tbl)
            c.execute(crt_mutes_tbl)

        # If an error occurs, it will be reported to the terminal with the
        # error printed.
        except Error as e:
            print ('Unable to create user.db quotes table\n' + str(e))

# Create or update server/channel/user/etc.
def fix_server(guild):
    conn = connect_to_db()
    id = guild.id
    name = guild.name

    with conn:
        c = conn.cursor()
        q_server = ''' SELECT * FROM servers WHERE id = ? '''
        c.execute(q_server, (id,))
        fetch = c.fetchall()
        server_exists = True
        if len(fetch) == 0:
            server_exists = False

        # If the server exists, we'll update it.
        if server_exists:
            sql = '''
                  UPDATE servers
                    SET name = ?
                  WHERE id = ?
                  '''

        # If the server doesn't exist, we'll create it.
        if not server_exists:
            sql = '''
                  INSERT INTO servers (name, id)
                  VALUES (?,?)
                  '''

        c.execute(sql, (name, id))

def fix_channel(channel):
    conn = connect_to_db()
    channel_id = channel.id
    server_id = channel.guild.id
    name = channel.name

    fix_server(channel.guild)

    with conn:
        c = conn.cursor()
        q_channel = ''' SELECT * FROM channels WHERE id = ? '''
        c.execute(q_channel, (channel_id,))
        fetch = c.fetchall()
        channel_exists = True
        if len(fetch) == 0:
            channel_exists = False

        # If the channel exists, we'll update it.
        if channel_exists:
            sql = '''
                  UPDATE channels
                    SET name = ?,
                        server = ?
                    WHERE id = ?
                  '''

        # If the channel doesn't exist, we'll create it.
        if not channel_exists:
            sql = '''
                  INSERT INTO channels (name, server, id)
                  VALUES (?,?,?)
                  '''

        c.execute(sql, (name, server_id, channel_id))


def fix_user(ctx):
    conn = connect_to_db()

    user_id = ctx.author.id
    server_id = ctx.guild.id
    discriminator = ctx.author.discriminator
    user_name = ctx.author.name
    user_disp_name = ctx.author.display_name
    avatar = ctx.author.avatar_url

    fix_server(ctx.guild)

    with conn:
        c = conn.cursor()
        q_user = ''' SELECT * FROM users WHERE id=? AND server=? '''
        c.execute(q_user, (user_id,server_id))
        fetch = c.fetchall()
        user_exists = True
        if len(fetch) == 0:
            user_exists = False

        # If the user exists, we'll update it.
        # Discriminator can change if they have nitro for example.
        if user_exists:
            sql = '''
                  UPDATE users
                    SET disp_name = ?,
                        discriminator = ?,
                        name = ?,
                        avatar = ?
                    WHERE id = ? AND server = ?
                  '''

        if not user_exists:
            sql = '''
                  INSERT INTO users (disp_name, discriminator, avatar, name, id, server)
                  VALUES (?,?,?,?,?,?)
                  '''

        try:
            c.execute(sql, (user_disp_name, discriminator, avatar, user_name, user_id, server_id))
        except Error as e:
            print(e)


def fix_mute(user, duration, is_delete):
    conn = connect_to_db()

def fix_rps(user):
    conn = connect_to_db()

# Quote-related commands.
def quote_embed(db_entry):
    conn = connect_to_db()
    db_entry = db_entry[0]
    id         = db_entry[0]
    quoter_id  = db_entry[1]
    quotee_id  = db_entry[2]
    server_id  = db_entry[3]
    channel_id = db_entry[4]
    date_said  = db_entry[5]
    content    = db_entry[6]

    # Getting some variables.
    with conn:
        c = conn.cursor()
        u_sql = ''' SELECT * FROM users WHERE id = ? AND server = ? '''
        c.execute(u_sql, (quoter_id, server_id))
        quoter_tuple = c.fetchall()[0]
        c.execute(u_sql, (quotee_id, server_id))
        quotee_tuple = c.fetchall()[0]

    # dname is displayname
    quoter_dname = quoter_tuple[2]
    quotee_dname = quotee_tuple[2]
    # hashname is user_name#discriminator, ex. TerminalNode#5986
    quoter_hashname = (quoter_tuple[3] + '#' + str(quoter_tuple[5]))
    quotee_hashname = (quotee_tuple[3] + '#' + str(quotee_tuple[5]))
    # avatar urls
    quoter_avatar = quoter_tuple[4]
    quotee_avatar = quotee_tuple[4]

    # combined_name is dname (hashname)
    # Super Terminal (TerminalNode#5986)
    # quoter_combined_name = ('%s (%s)' % (quoter_dname, quoter_hashname))
    # quotee_combined_name = ('%s (%s)' % (quotee_dname, quotee_hashname))


    embed = discord.Embed(color=0x00dee9)
    embed.set_author(name = quotee_dname, icon_url = quotee_avatar)
    embed.add_field(name = ('Posted on: ' + date_said), value = content)
    embed.set_footer(icon_url = quoter_avatar, text=("Added by " + quoter_dname + ' (Quote ID: ' + str(id) + ')'))

    return embed



def crt_quote(ctx, quote):
    conn = connect_to_db()
    id        = quote.id
    quoter    = ctx.author.id
    quotee    = quote.author.id
    server    = quote.guild.id
    channel   = quote.channel.id
    date_said = '{:%Y-%m-%d at %H:%M}'.format(quote.created_at)
    content   = quote.content

    print ('Check: crt_quote 1')
    fix_user(ctx)
    print ('Check: crt_quote 2')
    fix_user(quote)
    print ('Check: crt_quote 3')
    fix_channel(quote.channel)
    print ('Check: crt_quote 4')

    with conn:
        c = conn.cursor()

        q_quote = ''' SELECT * FROM quotes WHERE id = ? '''
        c.execute(q_quote, (id,))
        fetch = c.fetchall()
        quote_exists = True
        if len(fetch) == 0:
            quote_exists = False

        print('Check: crt_quote 5')

        if not quote_exists:
            sql =   '''
                    INSERT INTO quotes (id, quoter, quotee, server, channel, date_said, content)
                    VALUES (?,?,?,?,?,?,?)
                    '''
            try:
                print ('Check: crt_quote 6')
                c.execute(sql, (id, quoter, quotee, server, channel, date_said, content))
                print ('Check: crt_quote 7')
                c.execute('SELECT * FROM quotes WHERE id = ?', (c.lastrowid,))
                new_entry = c.fetchall()
            except Error as e:
                print(e)

    # Now we're ready for out return values
    if not quote_exists:
        print ('Check: crt_quote 8 (quote created!)')
        print ('New entry: ', new_entry)
        return quote_embed(new_entry)
    else:
        print ('Check: crt_quote 8 (quote not created)')
        return False

def get_quote_id(id, name):
    conn = connect_to_db()

def get_quote_rnd(id, is_name):
    conn = connect_to_db()
