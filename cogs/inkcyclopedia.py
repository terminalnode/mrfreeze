import discord                  # Basic discord functionality
import csv                      # Required for parsing the list of inks
import os                       # To check if an inkfile already exists
from airtable import airtable   # To update the inkdatabase, which is stored on airtable
from internals import checks    # Only owner is allowed to update the ink database

# Small script listening to all incoming messages looking for
# mentions of inks. Based on The Inkcyclopedia by klundtasaur:
# https://www.reddit.com/r/fountainpens/comments/5egjsa/klundtasaurs_inkcyclopedia_for_rfountainpens/
def setup(bot):
    bot.add_cog(InkcyclopediaCog(bot))

class InkcyclopediaCog(discord.ext.commands.Cog, name='Inkcyclopedia'):
    """Type an ink inside {curly brackets} and I'll tell you what it looks like!"""
    def __init__(self, bot):
        self.bot = bot
        self.inkydb = list()
        self.inkdb_path = "databases/dbfiles/inkcyclopedia.csv"
        self.inkdb_enc = "utf-8-sig"
        self.airtable = None

        # File config/airtable should have format:
        # base = <your base id here>
        # table = <your table name here>
        # apikey = <your api_key here>
        try:
            with open("config/airtable", "r") as airtable_file:
                content = [ i.split("=") for i in airtable_file.readlines() ]
                content = [ [i[0].strip(), i[1].strip()] for i in content ]
                keys = { i[0] : i[1] for i in content }
                self.airtable = airtable.Airtable(
                        keys["base"],
                        keys["table"],
                        api_key = keys["apikey"]
                )
        except:
            self.cog_unload()

    @discord.ext.commands.Cog.listener()
    async def on_ready(self):
        # Fetch inks if db does not exist
        if not os.path.isfile(self.inkdb_path):
            await self.fetch_inks()

        # Load up the ink db!
        await self.update_db()

        # Print that the ink database has been loaded and with how many inks.
        print('\033[0;36mThe ink database has been loaded with \033[35;1m{} inks\033[0;36m!\033[0m'.format(str(len(self.inkydb))))

    async def fetch_inks(self):
        with open(self.inkdb_path, "w", encoding=self.inkdb_enc) as inkfile:
            fetch = self.airtable.get_all()
            writer = csv.writer(inkfile)
            for row in fetch:
                try:
                    fields = row["fields"]
                    to_file = [ fields["Ink Name"], fields["RegEx"], fields["Inkbot version"] ]
                    writer.writerow(to_file)
                except:
                    pass

    async def update_db(self):
        with open(self.inkdb_path, encoding=self.inkdb_enc) as inkfile:
            reader = csv.reader(inkfile)

            for row in reader:
                ink_name = row[0]
                regex    = row[1]
                url      = row[2]
                self.inkydb.append((ink_name, regex, url))


    @discord.ext.commands.command(name="inkupdate")
    @discord.ext.commands.check(checks.is_owner)
    async def inkupdate(self, ctx):
        await self.fetch_inks()
        await self.update_db()
        await ctx.send(f"There are now {len(self.inkydb)} inks in the database!")

    @discord.ext.commands.Cog.listener()
    async def on_message(self, message):
        pass
