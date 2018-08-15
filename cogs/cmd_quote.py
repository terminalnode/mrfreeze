import discord, re
from discord.ext import commands
from botfunctions import userdb, checks

# This cog is for the !quote command.
# Mods are able to add quotes to the list.
# Users are able to have the bot cite random
# quotes that have previously been added.

class QuoteCmdCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='quote', aliases=['quotes'])
    async def _quote(self, ctx, *args):
        # First we'll see if the user has entered a number
        # i.e. a message ID.
        got_id = False
        if len(args) >= 1 and args[0].isdigit():
            message_id = args[0]
            got_id = True

        # For ease of use there are a number of aliases for each command.
        add_commands = ('add',)
        name_commands = ('name', 'shortcut', 'alias')
        remove_commands = ('remove', 'delete', 'erase')
        random_commands = ('random', 'rnd', 'any', 'whatever', 'anything')
        read_commands = ('read', 'cite', 'lookup', 'number', 'name')
        help_commands = ('help', 'how', 'howto')

        # Let's make sure the database exists.
        userdb.create()

        # Now we'll define the different functions which will execute once
        # we've figured out the command.
        async def add_quote(id):
            nonlocal ctx
            # We need to find the post with the correct ID to add it.
            msg = False
            for channel in ctx.guild.text_channels:
                try:
                    msg = await channel.get_message(id)
                except:
                    pass

            if msg != False:
                new_quote = userdb.crt_quote(ctx, msg)
                await ctx.send(embed=new_quote)
            else:
                await ctx.send(ctx.author.mention + ' I wasn\'t able to find any quote with the id: ' + str(id))

        def name_quote():
            pass

        def remove_quote():
            pass

        def random_quote():
            pass

        def read_quote():
            pass

        # Finally, we'll try to execute one of the above functions.
        if len(args) == 0:
            pass

        await add_quote(479269483219910668)



def setup(bot):
    bot.add_cog(QuoteCmdCog(bot))
