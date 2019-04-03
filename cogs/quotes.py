import discord, re, inflect
from discord.ext import commands
from botfunctions import userdb, checks
import traceback, sys

# This cog is for the !quote command.
# Mods are able to add quotes to the list.
# Users are able to have the bot cite random
# quotes that have previously been added.

class QuotesCog(commands.Cog):
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
        commands_dict = {
        'add'    : ('add', 'ajouter', 'ajoute', 'ajoutez', 'ajoutons', 'adda'),
        'alias'  : ('name', 'shortcut', 'alias'),
        'delete' : ('remove', 'delete', 'erase', 'del', 'rmv', 'undo'),
        'random' : ('random', 'rnd', 'any', 'whatever', 'anything'),
        'read'   : ('read', 'cite', 'lookup', 'number', 'name', 'by', 'from'),
        'count'  : ('count', 'number', 'quantity'),
        'help'   : ('help', 'how', 'howto', 'wtf', 'wut', 'halp')
        }

        # Below are the different functions which will execute once
        # we've figured out the desired command.

        ####################
        ### ADD QUOTE
        ####################
        async def add_quote(id):
            # We need to find the post with the correct ID to add it.
            msg = False
            for channel in ctx.guild.text_channels:
                try:
                    msg = await channel.get_message(id)
                except:
                    pass # this means the id wasn't in that channel

            if msg != False:
                new_quote = userdb.crt_quote(ctx, msg)
                if new_quote != None:
                    await ctx.send(('%s The requested post has been added to the quotes database:' % (ctx.author.mention,)), embed=new_quote)
                else:
                    await ctx.send('%s That quote is already in the database.' % (ctx.author.mention,))
            else:
                await ctx.send('%s I wasn\'t able to find any post with the id: %s' % (ctx.author.mention, str(id)))

        ####################
        ### NAME QUOTE (ASSIGN ALIAS TO)
        ####################
        async def name_quote(id, alias):
            # We don't allow aliases that are all digits.
            if (str(alias)).isdigit():
                await ctx.send('%s You\'re not allowed to pick an alias that\'s all digits. Pick a real alias, smud.' % (ctx.author.mention,))

            else:
                found, updated, old_alias = userdb.name_quote(id, alias)

                if found and updated:
                    # Alternative 1:
                    # All went smoothly.
                    if old_alias != None and old_alias != str():
                        await ctx.send('%s The alias was changed from **%s** to **%s**!' % (ctx.author.mention, str(old_alias), alias))
                    else:
                        await ctx.send('%s The alias **%s** was assigned to the requested quote.' % (ctx.author.mention, alias))

                elif found and not updated:
                    # Alternative 2:
                    # Found but couldn't update.
                    if old_alias == alias:
                        await ctx.send('%s That quote already has the alias **%s**!' % (ctx.author.mention, alias))
                    else:
                        await ctx.send('%s I found the quote, but for some reason I wasn\'t able to update the alias. Sorry.' % (ctx.author.mention,))

                elif not found:
                    # Alternative 3:
                    # The quote wasn't found.
                    await ctx.send('%s I can\'t find that quote and thus can\'t assign an alias to it!' % (ctx.author.mention,))

        ####################
        ### REMOVE/DELETE QUOTE
        ####################
        async def delete_quote(id):
            id = str(id)
            quote = userdb.delete_quote(id)

            # If quote is a tuple it means error.
            # If it's not it means it's an embed.
            if isinstance(quote, tuple):
                found, multiple = quote
                if found and multiple:
                    await ctx.send('%s I found multiple matches with that alias or id, so I didn\'t delete anything. My bad, this shouldn\'t happen...' % (ctx.author.mention,))

                elif not found:
                    await ctx.send('%s The alias or id you provided didn\'t return any matches, so I haven\'t deleted anything.' % (ctx.author.mention,))

            else:
                await ctx.send(('%s Success! The following quote was deleted:' % (ctx.author.mention,)), embed=quote)

        ####################
        ### RANDOM QUOTE
        ####################
        async def random_quote(id, quote):
            if quote == None:
                if id != None:
                    quote = userdb.get_quote_rnd(str(id))
                else:
                    quote = userdb.get_quote_rnd(None)

            # Found quote!
            if (quote != None):
                await ctx.send(('%s Here\'s a random quote for you!' % (ctx.author.mention,)), embed=quote)

            # Found no quote with chosen ID.
            elif (quote == None) and (id != None):
                await ctx.send('%s I couldn\'t find any quotes by the mentioned user.' % (ctx.author.mention,))

            # Found no quotes in the database.
            elif (quote == None) and (id == None):
                await ctx.send('%s There doesn\'t seem to be any quotes in the database. Perhaps consider adding one?' % (ctx.author.mention,))

        ####################
        ### READ QUOTE
        ####################
        async def read_quote(id, quote):
            if quote == None:
                id = str(id)
                quote = userdb.get_quote_id(id)

            if quote != None:
                await ctx.send(('%s Here\'s the quote you requested:' % (ctx.author.mention,)),embed=quote)
            else:
                await ctx.send('%s Sorry I couldn\'t find any quote by the alias/id **%s**!' % (ctx.author.mention, id))

        ####################
        ### COUNT QUOTES
        ####################
        async def count_quotes(id):
            infl = inflect.engine()
            if id != None:
                id = str(id)
                count, quote = userdb.count_quotes(id)

                if count == 0:
                    await ctx.send('%s That user has yet to say anything quote worthy.' % (ctx.author.mention,))
                elif count == 1:
                    await ctx.send(('%s There\'s a single quote attributed to that user, and that\'s this one:' % (ctx.author.mention,)), embed=quote)
                else:
                    await ctx.send('%s There are %s quotes attributed to that user.' % (ctx.author.mention, infl.number_to_words(count)))
            else:
                count, quote = userdb.count_quotes(None)
                if count == 0:
                    await ctx.send('%s No one\'s said anything quote worthy yet.' % (ctx.author.mention,))
                elif count == 1:
                    await ctx.send(('%s There\'s only a single quote in the database, and that\'s this one:' % (ctx.author.mention,)), embed=quote)
                else:
                    await ctx.send('%s There are %s quotes in the database right now.' % (ctx.author.mention, infl.number_to_words(count)))


        ####################################################################################
        # First we'll check for oddly formed arguments, these come in multiple categories  #
        #                           as is listed below.                                    #
        # No arguments    : Random quote.                                                  #
        # Only mentions   : Random quote by first mention.                                 #
        # Single argument : 1. Check if it's a command.                                    #
        #                       1.1. Check if the command can be called with               #
        #                            a single argument.                                    #
        #                      (1.2. Actual triggering of the command comes later.)        #
        #                   2. Check if it's an existing quote id or alias.                #
        #                   3. Check if it's a user ID from which we can retrieve a quote. #
        #                   4. Check if it's a post ID which we can add to the database.   #
        ####################################################################################

        number_of_args = len(args)
        # Defaults
        sent_reply = False
        chosen = None
        command = None

        # No arguments?
        if number_of_args == 0:
            await random_quote(None, None)
            sent_reply = True

        # Only mentions?
        elif (len(ctx.message.mentions) == len(args)) and (len(args) != 0):
            await random_quote(ctx.message.mentions[0].id, None)
            sent_reply = True

        # Attention: New if-clause.
        if not sent_reply:
            for command in commands_dict:
                if args[0] in commands_dict[command]:
                    chosen = command

        # If 'read' is specified without any additional arguments,
        # it will default to 'random'.
        if (chosen == 'read') and (number_of_args == 1):
            chosen = 'random'

        # Attention: New if-clause.
        if (chosen != None) and (sent_reply == False):
            if chosen == 'add':
                if (number_of_args >= 2) and (args[1].isdigit()):
                    await add_quote(args[1])
                    sent_reply = True

            elif chosen == 'alias':
                sent_reply = True
                if (number_of_args >= 3):
                    await name_quote(args[1], args[2])
                else:
                    await ctx.send('%s You need to type *!quote alias <id or old alias> <new alias>* for that to work!' % (ctx.author.mention,))

            elif chosen == 'delete':
                if (number_of_args >= 2):
                    await delete_quote(args[1])
                    sent_reply = True

            elif chosen == 'random':
                sent_reply = True
                if len(ctx.message.mentions) > 0:
                    await random_quote(ctx.message.mentions[0].id, None)
                else:
                    await random_quote(None, None)

            elif chosen == 'read':
                if (number_of_args >= 2):
                    sent_reply = True
                    if userdb.get_quote_id(args[1]) == None:
                        await random_quote(None, None)
                    else:
                        await read_quote(args[1], None)

            elif chosen == 'count':
                sent_reply = True
                if (len(ctx.message.mentions) > 0):
                    await count_quotes(ctx.message.mentions[0].id)
                else:
                    await count_quotes(None)

            elif chosen == 'help':
                sent_reply = True
                # TODO implement help thingie.
                await ctx.send(('%s Sorry the help command isn\'t implemented yet. You\'ll have to guess!' % (ctx.author.mention,)))

        # These three checks are as separate if-statements to avoid
        # accessing the database too many times.

        # Check if it's an existing quote id or alias.
        if chosen == None and sent_reply == False:
            quote  = userdb.get_quote_id(args[0])
            if quote != None:
                await read_quote(None, quote)
                sent_reply = True

        # Check if it's a user ID from which we can retrieve a quote.
        if chosen == None and sent_reply == False:
            quote = userdb.get_quote_rnd(args[0])
            if quote != None:
                await random_quote(None, quote)
                sent_reply = True

        # Check if it's a post ID from which we can create a new quote.
        if chosen == None and sent_reply == False:
            await add_quote(args[0])
            sent_reply = True

        # Finally, if nothing has triggered by now we have no idea wtf they're trying to do.
        if (command == None) and (sent_reply == False):
            await ctx.send(('%s Please consult the help file using **!help quote** because I have no idea wtf you\'re trying to do.' % (ctx.author.mention,)))

def setup(bot):
    bot.add_cog(QuotesCog(bot))
