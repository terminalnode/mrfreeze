import discord, re, datetime
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from botfunctions import native, checks, userdb

class UserCmdsCog():
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        # Creating dict of all the region role ids
        self.region_ids = dict()
        for guild in self.bot.guilds:
            self.region_ids[guild.id] = {
            'Africa':           discord.utils.get(guild.roles, name='Africa'),
            'North America':    discord.utils.get(guild.roles, name='North America'),
            'South America':    discord.utils.get(guild.roles, name='South America'),
            'Asia':             discord.utils.get(guild.roles, name='Asia'),
            'Europe':           discord.utils.get(guild.roles, name='Europe'),
            'Middle East':      discord.utils.get(guild.roles, name='Middle East'),
            'Oceania':          discord.utils.get(guild.roles, name='Oceania'),
            'Antarctica':       discord.utils.get(guild.roles, name='Antarctica')
            }

    @commands.command(name='rules', aliases=['rule'])
    async def _rules(self, ctx, *args):
        request = str()
        for i in args:
            request += (i.lower())

        rules = {
        1: ( '1', 'topic', 'ontopic', 'offtopic' ),
        2: ( '2', 'civil', 'disagreement' ),
        3: ( '3', 'dismissive', 'opinion', 'opinions' ),
        4: ( '4', 'joke', 'jokes', 'joking', 'sex', 'sexual',
             'orientation', 'weight', 'race', 'skin', 'color',
             'gender', 'colour' ),
        5: ( '5', 'shoe', 'shoes', 'age', 'mature', 'maturity', 'shoesize', 'act' ),
        6: ( '6', 'spam', 'nonsense' ),
        7: ( '7', 'benice', 'nice' )
        }

        called_rules = list()

        # If 'all' is in the request we'll just call all rules.
        # If not we'll see if any of the keywords are in the request.
        if 'all' in request:
            called_rules = [ 1, 2, 3, 4, 5, 6, 7 ]
        else:
            for rule_no in rules:
                for keyword in rules[rule_no]:
                    if keyword in request and rule_no not in called_rules:
                        called_rules.append(rule_no)

        if len(called_rules) == 0:
            replystr = 'Sorry %s, your terms don\'t seem to match any rules. :thinking:'
            await ctx.send(replystr % (ctx.author.mention,))
        else:
            await ctx.send(ctx.author.mention + '\n' + native.get_rule(called_rules))

    @commands.command(name='mrfreeze', aliases=['freeze'])
    async def _mrfreeze(self, ctx, *args):
        # If they're asking for help, we'll default to the help_reply.
        pls_help = ('help', 'wtf', 'what', 'what\'s', 'wut', 'woot')
        help_reply = False
        for i in pls_help:
            if i in args:
                help_reply = True

        # If they say the bot sucks, we'll default to the suck_reply.
        you_suck = ('sucks', 'suck', 'blows', 'blow')
        suck_reply = False
        for i in you_suck:
            if i in args:
                suck_reply = True

        # If they're telling the bot to kill itself... well...
        death_reply = False
        passive_die = ('die', 'suicide')
        for i in args:
            if i in passive_die:
                death_reply = True

        active_die  = ('kill', 'murder', 'destroy')
        yourself_spells = ('yourself', 'urself', 'uself', 'u', 'you')
        for i in active_die:
            for k in yourself_spells:
                if i and k in args:
                    death_reply = True

        if help_reply:
            replystr = ('Allow me to break the ice: My name is Freeze and the command **!mrfreeze** ' +
                        ' will have me print one of my timeless quotes from Batman & Robin.')
            await ctx.send(replystr)
        elif suck_reply:
            replystr = 'Freeze in hell, %s!'
            await ctx.send(replystr % (ctx.author.mention,))
        elif death_reply:
            replystr = '%s You\'re not sending *ME* to the *COOLER*!'
            await ctx.send(replystr % (ctx.author.mention,))
        else:
            quote = native.mrfreeze()
            quote = quote.replace('Batman', ctx.author.mention)
            quote = quote.replace('Gotham', ('**' + ctx.guild.name + '**'))
            await ctx.send(quote)

    @commands.command(name='vote', aliases=['election', 'choice', 'choose'])
    async def _vote(self, ctx, *args):
        # remoji finds custom emoji strings which have the form:
        # <:trex:463347402242260993>
        remoji = re.compile('<:\w+:\d+>')

        # remojid finds a string starting with :, having an arbitrary number
        # of digits and ending with a >. In the example above this would be:
        # :463347402242260993>
        # We need the : and > in case the emoji code/name is all numbers.
        remojid = re.compile(':\d+>')

        # skipping first line because we don't need it
        if '\n' in ctx.message.content:
            lines = ctx.message.content.split('\n')[1:]
            single_line = False
        else:
            lines = ['error',]
            single_line = True

        # Step 1: Try to react with the first character on the line.
        # Step 2: Use regex to try and find a custom emoji.
        # Step 3: If one is found, extract the emoji ID and get the object.
        added_reacts = list()
        success = False
        for line in lines:
            # This try-except thing is step 1, i.e. for simple ISO standard emoji.
            try:
                if line[0] not in added_reacts:
                    await ctx.message.add_reaction(line[0])
                    added_reacts.append(line[0])
                    success = True
            except:
                pass

            # This try-except thing is step 2, which finds custom emoji.
            match = remoji.match(line)
            if not isinstance(match, type(None)):
                # Because the remojiid also grabs the : and > we only want [1:-1]
                match_id = int(remojid.search(match.group()).group()[1:-1])
                emoji = discord.utils.get(ctx.guild.emojis, id=match_id)
                try:
                    if match_id not in added_reacts:
                        await ctx.message.add_reaction(emoji)
                        added_reacts.append(match_id)
                        success = True
                except:
                    pass

        if success:
            replystr = '%s That\'s such a great proposition I voted for everything!'
            await ctx.send(replystr % (ctx.author.mention))
        elif single_line:
            replystr = '%s You need at least two lines to create a vote you filthy smud.'
            await ctx.send(replystr % (ctx.author.mention))
        else:
            replystr = '%s There\'s literally nothing I can vote for in your smuddy little attempt at a vote! :rofl:'
            await ctx.send(replystr % (ctx.author.mention,))

    @commands.command(name='region', aliases=['regions'])
    async def _region(self, ctx, *args):
        region_ids = self.region_ids
        # List of regions
        regions = {
        'Africa':        ('africa',),
        'North America': ('north america', 'usa', 'united states', 'canada', 'mexico', 'us', 'na'),
        'South America': ('south america', 'argentina', 'brazil', 'chile', 'peru', 'sa'),
        'Asia':          ('asia', 'china', 'taiwan', 'japan', 'nihon', 'nippon', 'korea'),
        'Europe':        ('europe', 'great britain', 'france', 'united kingdom', 'gb', 'uk',
                          'sweden', 'denmark', 'norway', 'finland', 'scandinavia', 'poland',
                          'italy', 'germany', 'russia', 'spain', 'portugal', 'hungary'),
        'Middle East':   ('middle east', 'middle-east', 'mesa', 'ksa', 'saudi'),
        'Oceania':       ('oceania', 'australia', 'zealand', 'zeeland')
        }

        ### See if the user wants to blacklist someone
        add_blacklist_alias = ('blacklist', 'black', 'bl', 'ban', 'forbid')
        rmv_blacklist_alias = ('unblacklist', 'unblack', 'unbl', 'unban', 'unforbid', 'allow', 'remove')

        add_blacklist = False
        rmv_blacklist = False
        for alias in add_blacklist_alias:
            if (' ' + alias) in ctx.message.content:
                add_blacklist = True

        for alias in rmv_blacklist_alias:
            if (' ' + alias) in ctx.message.content:
                rmv_blacklist = True

        ### See if the user wants a list of regions
        list_regions = ('list', 'regions', 'available')
        give_list = False
        for alias in list_regions:
            if (' ' + alias) in ctx.message.content:
                give_list = True

        ### See if the user mentioned antarctica.
        antarctica_choice = False
        antarctica_spelling = False
        antarctica = ('antarctica', 'antarctic', 'antartica', 'anctartctica', 'antartic', 'anarctica')
        spelling = ''
        for alias in antarctica:
            if (' ' + alias + ' ') in (ctx.message.content.lower() + ' '):
                antarctica_choice = True
                if (alias != 'antarctica') and (alias != 'antarctic'):
                    antarctica_spelling = True
                    spelling = alias
        if not antarctica_spelling:
            spelling = 'antarctic(a)'

        ### See if the user is a mod, if they're not see if they're blacklisted.
        is_mod = await checks.is_mod(ctx.author)
        if not is_mod:
            is_blacklisted = userdb.is_blacklisted(ctx.author)
        else:
            is_blacklisted = False

        # Now we'll execute our command.
        # Only one command will be executed and they will be executed in
        # in the following order:
        # - antarctica
        # - conflicting blacklist (if we have both)
        # - remove blacklist
        # - add blacklist,
        # - block user due to blacklisting
        # - list regions
        # - assign a region

        if antarctica_choice:
            if antarctica_spelling:
                # 20 minutes for incorrect spelling.
                end_time = datetime.datetime.now() + datetime.timedelta(minutes=20)
            else:
                # 10 minutes for correct spelling.
                end_time = datetime.datetime.now() + datetime.timedelta(minutes=10)

            # Adding the user to is_muted table. This action is not voluntary.
            # fix_mute(user, voluntary=False, until=None, delete=False)
            prolonged = userdb.prolong_mute(ctx.author, until=end_time)

            # Adding the role, if unsuccessful see what caused the error
            try:
                await ctx.author.add_roles(self.region_ids[ctx.guild.id]['Antarctica'], reason=('User issued !region ' + spelling))
                success = True
            except discord.Forbidden:
                success = False
                reason = ('Lacking permissions to change role.')
            except discord.HTTPException:
                success = False
                reason = ('Error connecting to discord.')

            if success:
                if not antarctica_spelling:
                    # Correct spelling.
                    if prolonged:
                        replystr = '%s is a filthy smud claiming to live in Antarctica... '
                        replystr += 'oh and they do. Well if they like it so much I guess '
                        replystr += 'prolonging their sentence another TEN minutes won\'t hurt?'
                    else:
                        replystr = ('%s is a filthy smud claiming to live in Antarctica, ' +
                                    'their wish has been granted and they will be stuck there for about TEN minutes!')
                    await ctx.send(replystr % (ctx.author.mention,))

                else:
                    # Incorrect spelling
                    if prolonged:
                        replystr = '%s can\'t even spell \'%s\' right despite living there! Maybe an '
                        replystr += 'extra TWENTY minutes in penguin school will set \'em straight? :penguin:'
                    else:
                        replystr = ('%s is a filthy smud claiming to live in \'%s\'! They couldn\'t even spell it right ' +
                                    'and because of that they\'ll be stuck there for about TWENTY minutes!')
                    await ctx.send(replystr % (ctx.author.mention, spelling))

            else:
                # Failed to add role.
                replystr = ('%s is a filthy smud claiming to live in Antarctica, but I couldn\'t banish them there due to:\n%s')
                await ctx.send(replystr % (ctx.author.mention, reason))

        elif add_blacklist or rmv_blacklist:
            if not is_mod:
                # If the user is not mod, they're not allowed to touch the blacklist.
                # This will earn them 15 minutes in Antarctica.
                end_time = datetime.datetime.now() + datetime.timedelta(minutes=15)
                prolonged = userdb.prolong_mute(ctx.author, until=end_time)
                try:
                    await ctx.author.add_roles(self.region_ids[ctx.guild.id]['Antarctica'], reason=('User issued !region ' + spelling))
                    success = True
                except discord.Forbidden:
                    success = False
                    reason = ('Lacking permissions to change role.')
                except discord.HTTPException:
                    success = False
                    reason = ('Error connecting to discord.')

                if success:
                    if prolonged:
                        replystr = '%s Smuds like you are not allowed to edit the blacklist, this misdemeanor '
                        replystr += 'has *prolonged* your time in Antarctica by FIFTEEN minutes!'
                        await ctx.send(replystr % (ctx.author.mention,))
                    else:
                        replystr = ('%s Smuds like you are not allowed to edit the blacklist. ' +
                                    'This misdemeanor has earned you about FIFTEEN minutes in Antarctica!')
                        await ctx.send(replystr % (ctx.author.mention,))
                else:
                    replystr = ('%s Smuds like you are not allowed to neither remove nor add entries to the blacklist.\n' +
                                'Normally this would earn you FIFTEEN minutes in Antarctica, but I failed to banish you due to:\n%s')
                    await ctx.send(replystr % (ctx.author.mention, reason))

            elif add_blacklist and rmv_blacklist:
                # Conflicting messages, not sure if we're supposed to add or remove.
                replystr = '%s I\'m getting mixed messages, I\'m not sure if you want to remove or add entries to the blacklist.'
                await ctx.send(replystr % (ctx.author.mention,))

            elif len(ctx.message.mentions) == 0:
                # We can't do this without any mentions.
                replystr = ('%s You want to edit the blacklist, but you failed to mention anyone. ' +
                            'You\'re a huge disappointment to modkind, please never talk to me again.')
                await ctx.send(replystr % (ctx.author.mention,))


            else:
                # Else means that:
                # - we have add_blacklist or rmv_blacklist but not both.
                # - user is mod.
                # - at least one person was mentioned.

                # userdb.fix_blacklist takes the boolean argument 'add'
                # to know if it's gonna add or delete entries.
                if add_blacklist:
                    action = True
                else:
                    action = False

                # Who was added and who wasn't?
                list_of_fails = list()
                list_of_successes = list()

                for user in ctx.message.mentions:
                    success, blacklisted = userdb.fix_blacklist(user, add=action)
                    if success:
                        list_of_successes.append(user)
                    else:
                        list_of_fails.append(user)

                fails_tally = len(list_of_fails)
                total_tally = len(ctx.message.mentions)
                fails_str = native.mentions_list(list_of_fails)
                success_str = native.mentions_list(list_of_successes)

                if add_blacklist:
                    if total_tally == 1 and fails_tally == 0:
                        # One total and succeeded.
                        replystr = '%s The filthy region abusing smud %s has been banned from changing their region.'
                        await ctx.send(replystr % (ctx.author.mention, success_str))

                    elif total_tally == 1 and fails_tally == 1:
                        # One total and failed.
                        replystr = ('%s I wasn\'t able to add %s to the list of smuds '
                                   'banned from changing their region. Perhaps they\'re already on the list?')
                        await ctx.send(replystr % (ctx.author.mention, fails_str))

                    elif total_tally > 1 and fails_tally == 0:
                        # More than one and all succeeded.
                        replystr = '%s The filthy region abusing smuds %s have been banned from changing their region.'
                        await ctx.send(replystr % (ctx.author.mention, success_str))

                    elif total_tally > 1 and fails_tally > 0:
                        # More than one and at least one fail.
                        replystr = ('%s I wasn\'t able to add all of the requested users to the list ' +
                                    'of smuddy region abusers, perhaps some of them were already there?' +
                                    '\nBlacklisted: %s\nNot blacklisted: %s')
                        await ctx.send(replystr % (ctx.author.mention, success_str, fails_str))

                elif rmv_blacklist:
                    if total_tally == 1 and fails_tally == 0:
                        # One total and succeeded.
                        replystr = '%s The user %s is once again allowed to change their region.'
                        await ctx.send(replystr % (ctx.author.mention, success_str))

                    elif total_tally == 1 and fails_tally == 1:
                        # One total and failed.
                        replystr = ('%s I wasn\'t able to remove %s from the list of smuds ' +
                                   'banned from changing their region. Perhaps they\'re already off the list?')
                        await ctx.send(replystr % (ctx.author.mention, fails_str))

                    elif total_tally > 1 and fails_tally == 0:
                        # More than one and all succeeded.
                        replystr = '%s The users %s are once again allowed to change their regions.'
                        await ctx.send(replystr % (ctx.author.mention, success_str))

                    elif total_tally > 1 and fails_tally > 0:
                        # More than one and at least one fail.
                        replystr = ('%s I wasn\'t able to remove all of the requested users from the list of smuddy region abusers, ' +
                                   'perhaps some of them were already removed?\nUnblacklisted: %s\nNot unblacklisted: %s')
                        await ctx.send(replystr % (ctx.author.mention, success_str, fails_str))

        elif is_blacklisted:
            replystr = ('%s Smuds like you are why we can\'t have nice things, or rather...' +
                       'why you can\'t have nice things. The *privilege* of changing your own' +
                       'region has been revoked from you.')
            await ctx.send(replystr % (ctx.author.mention))

        elif give_list:
            # Print a list of all the available regions.
            replystr = ('%s The available regions are:\n' +
                           '- Africa\n' +
                           '- North America\n' +
                           '- South America\n' +
                           '- Antarctica\n' +
                           '- Asia\n' +
                           '- Europe\n' +
                           '- Middle-East\n' +
                           '- Oceania')
            await ctx.send(replystr % (ctx.author.mention,))

        else:
            # List of region_ids from role abc's in region_ids[guild.id], except for Antarctica.
            region_ids = [ self.region_ids[ctx.guild.id][region].id for region in self.region_ids[ctx.guild.id] if region != 'Antarctica' ]
            # Author role ids minus the ones in region_ids
            old_author_roles = [ i.id for i in ctx.author.roles ]
            new_author_roles = [ i.id for i in ctx.author.roles if i.id not in region_ids ]

            match = list()
            for region in regions:
                for alias in regions[region]:
                    if (' ' + alias + ' ') in (ctx.message.content.lower() + ' '):
                        match = [region, self.region_ids[ctx.guild.id][region].id]

            if len(match) == 0:
                replystr = '%s I couldn\'t find any match for the region you mentioned. Type !region list for a list of available regions.'
                await ctx.send(replystr % (ctx.author.mention,))

            elif match[1] in old_author_roles:
                replystr = '%s You\'re already in **%s**, wtf are you trying to do?'
                await ctx.send(replystr % (ctx.author.mention, match[0]))

            else:
                new_author_roles.append(match[1])

                for i in range(len(new_author_roles)):
                    new_author_roles[i] = discord.Object(id = new_author_roles[i])

                try:
                    await ctx.author.edit(roles=new_author_roles)
                    replystr = '%s You\'ve successfully been assigned a new region!\nWelcome to **%s**!'
                    await ctx.send(replystr % (ctx.author.mention, match[0]))
                except discord.Forbidden:
                    replystr = '%s I found a match for you, but I wasn\'t allowed to edit your roles due to insufficient privilegies. :sob:'
                    await ctx.send(replystr % (ctx.author.mention,))
                except discord.HTTPException:
                    replystr = '%s I found a match for you, but due to a connection error I wasn\'t able to edit your roles. :sob:'
                    await ctx.send(replystr % (ctx.author.mention,))

    @commands.command(name='activity', aliases=['listen', 'listening', 'playing', 'play', 'game', 'gaming', 'gameing', 'stream', 'streaming', 'watch', 'watching'])
    @commands.cooldown(1, (60*10), BucketType.default)
    async def _activity(self, ctx, *args):
        # Dictionary of all different activity types with keywords.
        # The keywords are defined in separate tuples so I can access
        # them without the dictionary.
        play_words   = ('play','playing', 'game', 'gaming', 'gameing')
        stream_words = ('stream', 'streaming')
        listen_words = ('listen', 'listening')
        watch_words  = ('watch', 'watching')

        activity_types = {
            None                           : ('activity',),
            discord.ActivityType.playing   : play_words,
            discord.ActivityType.streaming : stream_words,
            discord.ActivityType.listening : listen_words,
            discord.ActivityType.watching  : watch_words
        }

        # We will determine the chosen activity in one of two ways.
        # 1. By checking which alias they used.
        # 2. By seeing which arguments they tried.
        for type in activity_types:
            for alias in activity_types[type]:
                if alias == ctx.invoked_with:
                    chosen_activity = type

        # On to step 2, seeing which arguments they tried and
        # possibly identifying a type of activity.

        if chosen_activity == None:
            for type in activity_types:
                for alias in activity_types[type]:
                    if (len(args) >= 1) and (args[0] == alias):
                        chosen_activity = type
                        args = args[1:]

                    elif (len(args) >= 2) and (args[0] == 'is') and (args[1] == alias):
                        chosen_activity = type
                        args = args[2:]

        success = False
        max_activity_length = 30
        if len(args) != 0:
            joint_args = ' '.join(args)

            # If we haven't been able to identify an activity we'll default to listening:
            if chosen_activity == None:
                chosen_activity = discord.ActivityType.listening

            if len(joint_args) <= max_activity_length:
                try:
                    await self.bot.change_presence(status=None, activity=
                          discord.Activity(name=joint_args, type=chosen_activity))
                    success = True
                except:
                    pass

        if chosen_activity == discord.ActivityType.playing:
            reply_activity = 'playing'
        elif chosen_activity == discord.ActivityType.streaming:
            # streaming doesn't work as I want it, you need a URL and shit
            reply_activity = 'playing'
        elif chosen_activity == discord.ActivityType.listening:
            reply_activity = 'listening to'
        elif chosen_activity == discord.ActivityType.watching:
            reply_activity = 'watching'
        else:
            # Default activity.
            reply_activity = 'listening to'

        if success:
            replystr = '%s OK then, I guess I\'m **%s %s** now.'
            await ctx.send(replystr % (ctx.author.mention, reply_activity ,joint_args))

        elif len(args) == 0:
            if chosen_activity == None: # No activity specified.
                replystr = '%s You didn\'t tell me what to do.'
                await ctx.send(replystr % (ctx.author.mention,))

            else: # No name specified.
                replystr = '%s I can tell you want me to be **%s** something, but I don\'t know what.'
                await ctx.send(replystr % (ctx.author.mention, reply_activity))

        elif len(joint_args) >= max_activity_length: # Too long.
            replystr = '%s That activity is stupidly long. Limit is %s characters, yours was %s.'
            replystr = (replystr % (ctx.author.mention, str(max_activity_length), str(len(joint_args))))
            await ctx.send(replystr)

        else:
            replystr = '<@!154516898434908160> Something went wrong when trying to change my activity and I have no idea what. Come see!'
            await ctx.send(replystr)


def setup(bot):
    bot.add_cog(UserCmdsCog(bot))
