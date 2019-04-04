import discord, csv
from discord.ext import commands
from botfunctions import native

# Small script listening to all incoming messages looking for
# mentions of inks. Based on The Inkcyclopedia by klundtasaur:
# https://www.reddit.com/r/fountainpens/comments/5egjsa/klundtasaurs_inkcyclopedia_for_rfountainpens/

class InkcyclopediaCog(commands.Cog, name='Inkcyclopedia'):
    """Type an ink inside {curly brackets} and I'll tell you what it looks like!"""
    def __init__(self, bot):
        self.bot = bot
        self.inkydb = list()

    @commands.Cog.listener()
    async def on_ready(self):
        # Load up the ink db!
        with open('databases/inkcyclopedia.csv', encoding='utf-8-sig') as inkfile:
            inkdb = csv.reader(inkfile)

            for row in inkdb:
                status   = row[3]
                if 'Active' in status:
                    ink_name = row[0]
                    donator  = row[2]
                    regex    = row[4]
                    url      = row[5]
                    self.inkydb.append((ink_name, regex, url, donator))
            del inkdb

        # Print that the ink database has been loaded and with how many inks.
        print('\033[0;36mThe ink database has been loaded with \033[35;1m{} inks\033[0;36m!\033[0m'.format(str(len(self.inkydb))))

    @commands.Cog.listener()
    async def on_message(self, message):
        pass

def setup(bot):
    bot.add_cog(InkcyclopediaCog(bot))
