import discord, re, datetime
from discord.ext import commands
from botfunctions import checks, native, userdb

# This cog is for commands restricted to mods on a server.
# It features commands such as !ban, !mute, etc.

class ModCmdsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def extract_reason(self, reason):
        # This is a simple function that will return anything after the list of mentions.
        # It's extremely clunky, but it gets the job done.

        output = reason
        in_mention = False
        for letter in range(len(reason)):

            # If the current and two following characters form <@ and a digit, we
            # assume that we're in a mention.
            if (reason[letter:letter+2] == '<@') and (reason[letter+2].isdigit()):
                in_mention = True

            # If we're in a mention and detect the closing >, we'll add all trailing
            # characters to the output. These two steps are repeated until we have
            # an output void of any mentions.
            if in_mention and (reason[letter] == '>'):
                in_mention = False
                output = reason[(letter+1):]

        # If there's nothing left after these steps we'll return None.
        # Otherwise we'll return the output.
        if len(output.strip()) == 0:
            return None
        else:
            return output.strip()


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


    @commands.command(name='mute', aliases=['micromute', 'exile', 'banish', 'microexile', 'microbanish'])
    @commands.check(checks.is_mod)
    async def _banish(self, ctx, *args):
        # (micro)banish and (micro)exile are functionally the same as mute, except with a custom message
        # and default time limit. The idea for the micro prefix is that it will work more as a statement
        # and only banish the user for a minute or so.
        # Because the mechanics of these functions are so similar - i.e. add a tag and edit the database,
        # I've chosen to clump them into the same function.

        # Calling this with the (micro)exile or (micro)banish commands sets
        # is_banish to True and activates the custom message that comes with it.
        if ('exile' in ctx.invoked_with) or ('banish' in ctx.invoked_with):
            is_banish = True
        else:
            is_banish = False

        # Using any of the commands prefixed with micro or adding micro to the command
        # will make the action mostly symbolic, i.e. unmuteing them within about half a
        # minute or so (depending on where in the mute check cycle we are when the cmd is fired).
        if 'micro' in ctx.invoked_with:
            is_micro = True
        elif 'micro' in args:
            is_micro = True
        else:
            is_micro = False

        success_list = list()
        fail_list = list()
        mods_list = list()
        forbidden_error = False
        http_error = False
        antarctica = discord.utils.get(ctx.guild.roles, name='Antarctica')

        # For this function we'll need to analyse the arguments to find out
        # for how long they're gonna be muted. This function returns these values:
        # args, add_time, end_date
        # args are the args put into a string where the time statements have
        # been removed. add_time is how much time will be added. end_date
        # is the time at which the mute will come to an end local time.
        tstripped_args, add_time, end_date = native.extract_time(args)
        reason = self.extract_reason(tstripped_args)

        # If no time statements were found, we'll add our own.
        current_date = datetime.datetime.now()
        time_str = None
        if end_date == None and is_micro:
            add_time = datetime.timedelta(seconds=45)
            end_date = current_date + add_time
            time_str = 'a very short time'

        elif end_date== None and is_banish:
            add_time = datetime.timedelta(minutes=10)
            end_date = current_date + add_time
            time_str = '10 minutes'

        elif end_date == None:
            # Setting until=None makes the mute indefinite.
            end_date = None
            time_str = 'the forseeable future'

        if time_str == None:
            time_str = native.parse_timedelta(add_time)

        # You're not allowed to mute mods.
        # Unlike the kick command, this doesn't prevent
        # muteing all the other users.
        mod_role = discord.utils.get(ctx.guild.roles, name='Administration')
        mods_list = [ user for user in ctx.message.mentions if mod_role in user.roles ]
        ment_mods = native.mentions_list(mods_list)

        if len(mods_list) == 0:
            tried_to_mute_mod = False
        else:
            tried_to_mute_mod = True

        for victim in ctx.message.mentions:
            if (victim not in mods_list):
                try:
                    if reason == None:
                        await victim.add_roles(antarctica)
                        userdb.fix_mute(victim, until=end_date)
                        success_list.append(victim)

                    else:
                        await victim.add_roles(antarctica, reason=reason)
                        userdb.fix_mute(victim, until=end_date)
                        success_list.append(victim)

                except discord.Forbidden:
                    fail_list.append(victim)
                    forbidden_error = True

                except discord.HTTPException:
                    fail_list.append(victim)
                    http_error = True

        ### Now all we need to do is fix a reply.
        # There are two large categories of replies, banish and non-banish.
        # There are also two large categorios of errors, exceptions and mod errors.
        ment_success = native.mentions_list(success_list)
        ment_fail    = native.mentions_list(fail_list)
        ment_mods    = native.mentions_list(mods_list)

        # Error list:
        if forbidden_error and not http_error:
            error_str = 'Insufficient privilegies.'
        elif not forbidden_error and http_error:
            error_str = 'HTTP issues.'
        else:
            error_str = 'A mix of insufficient privilegies and HTTP issues.'

        if is_banish:
            if tried_to_mute_mod:
                if (len(ctx.message.mentions) == 1) and (ctx.author in ctx.message.mentions):
                    # Only tried to mute themselves.
                    replystr = '%s You tried to banish yourself! SAD!'
                    replystr = (replystr % (ctx.author.mention,))

                elif len(mods_list) == len(ctx.message.mentions):
                    # Only tried to mute mods.
                    replystr = '%s All the users you tried to banish are mods! Please try to get along...'
                    replystr = (replystr % (ctx.author.mention,))

                else:
                    # Tried to mute people other than mods, but also mods.

                    if (len(fail_list) == 0) and (len(success_list) == 1):
                        # No fails, singular success.
                        replystr = '%s It goes without saying that *mods are unbanishable*, however the smud %s will be banished to Antarctica for %s! :penguin:'
                        replystr = (replystr % (ctx.author.mention, ment_success, time_str))

                    elif (len(fail_list) == 0) and (len(success_list) > 1):
                        # No fails, plural success.
                        replystr = '%s *I\'m unable to banish mods*, however the smuds known as %s will be banished to Antarctica for %s! :penguin:'
                        replystr = (replystr % (ctx.author.mention, ment_success, time_str))

                    elif (len(fail_list) > 0) and (len(success_list) > 0):
                        # Mixed results: at least one fail and at least one success.
                        replystr = '%s *I know I can\'t banish mods*, but it seems I was only able to banish some of the smuds mentioned.'
                        replystr += '\n**Banished:** %s\n**Not Banished:** %s'
                        replystr += 'The banished will be stuck there for %s'
                        replystr += '\nMy diagnostics tell the error(s) were due to: %s'
                        replystr = (replystr % (ctx.author.mention, ment_success, ment_fail, time_str, error_str))

                    elif (len(fail_list) == 1) and (len(success_list) == 0):
                        # Singular fail, no success.
                        replystr = '%s I\'m so confused. Of course *I can\'t banish mods* but why couldn\'t I banish %s?\nIt might be due to: %s'
                        replystr = (replystr % (ctx.author.mention, ment_fail, error_str))

                    elif (len(fail_list) > 1) and (len(success_list) == 0):
                        # Plural fail, no success.
                        replystr = '%s Some higher power seems to have stripped me of my powers! *Mods are of course unbanishable*, but I was also '
                        replystr += 'unable to banish any of %s!\nMy diagnostics tells me this was due to: %s'
                        replystr = (replystr % (ctx.author.mention, ment_fail, error_str))

            elif not tried_to_mute_mod:
                if (len(ctx.message.mentions) == 0):
                    # Failed to mention anyone.
                    replystr = '%s You need to mention the people you want me to banish, fool.'
                    replystr = (replystr % (ctx.author.mention,))

                elif (len(fail_list) == 0) and (len(success_list) == 1):
                    # No fail, singular success.
                    replystr = '%s Excellent, %s is a smud who should\'ve been banished a long time ago if you ask me. They\'ll be stuck at '
                    replystr += 'sub-zero temperatures for %s. :penguin:'
                    replystr = (replystr % (ctx.author.mention, ment_success, time_str))

                elif (len(fail_list) == 0) and (len(success_list) > 1):
                    # No fail, plural success.
                    replystr = '%s Excellent, %s are smuds who should\'ve been banished a long time ago if you ask me. They\'ll be stuck at '
                    replystr += 'sub-zero temperatures for %s. :penguin:'
                    replystr = (replystr % (ctx.author.mention, ment_success, time_str))

                elif (len(fail_list) > 0) and (len(success_list) > 0):
                    # At least one fail and at least one success.
                    replystr = '%s I wasn\'t able to banish all of the users requested, however those that were banished will be stuck in Antarctica '
                    replystr += 'for %s. :penguin:\n**Banished:** %s\n**Not banished:** %s\nErrors were due to: %s'
                    replystr = (replystr % (ctx.author.mention, time_str, ment_success, ment_fail, error_str))

                elif (len(fail_list) == 1) and (len(success_list) == 0):
                    # Singular fail, no success.
                    error_str = error_str.lower().replace('.', '')
                    replystr = '%s Excellent decision! ...but nope. Due to %s %s will continue to roam free.'
                    replystr = (replystr % (ctx.author.mention, error_str, ment_fail))

                elif (len(fail_list) > 0) and (len(success_list) == 0):
                    # Plural fail, no success.
                    error_str = error_str.lower().replace('.', '')
                    replystr = '%s Excellent decision! ...but nope. Due to %s %s will continue to roam free.'
                    replystr = (replystr % (ctx.author.mention, error_str, ment_fail))

        elif not is_banish:
            if tried_to_mute_mod:
                if (len(ctx.message.mentions) == 1) and (ctx.author in ctx.message.mentions):
                    # Only tried to mute themselves.
                    replystr = '%s You tried to mute yourself! SAD!'
                    replystr = (replystr % (ctx.author.mention,))

                elif len(mods_list) == len(ctx.message.mentions):
                    # Only tried to mute mods.
                    replystr = '%s All the users you tried to mute are mods! Mods have diplomatic immunity...'
                    replystr = (replystr % (ctx.author.mention,))

                else:
                    # Tried to mute people other than mods, but also mods.

                    if (len(fail_list) == 0) and (len(success_list) == 1):
                        # No fails, singular success.
                        replystr = '%s The mod(s) mentioned can\'t be muted, but %s isn\'t a mod and will therefore be silenced for %s.'
                        replystr = (replystr % (ctx.author.mention, ment_success, time_str))

                    elif (len(fail_list) == 0) and (len(success_list) > 1):
                        # No fails, plural success.
                        replystr = '%s The mod(s) mentioned can\'t be muted for what I hope is obvious reasons, but %s aren\'t mods and will therefore be silenced for %s.'
                        replystr = (replystr % (ctx.author.mention, ment_success, time_str))

                    elif (len(fail_list) > 0) and (len(success_list) > 0):
                        # Mixed results: at least one fail and at least one success.
                        replystr = '%s You can\'t mute mods silly, and apparently not all of the smuds mentioned either...\n'
                        replystr += '**Muted:** %s\n**Not muted:** %s\n'
                        replystr += 'The error(s) seem to have been due to: %s\n'
                        replystr += 'The muted people will be muted for %s.'
                        replystr = (replystr % (ctx.author.mention, ment_success, ment_fail, error_str, time_str))

                    elif (len(fail_list) == 1) and (len(success_list) == 0):
                        # Singular fail, no success.
                        replystr = '%s The mod(s) mentioned can\'t be muted... but apparently neither can %s.\n'
                        replystr += 'This seems to be due to: %s'
                        replystr = (replystr % (ctx.author.mention, ment_fail, error_str))

                    elif (len(fail_list) > 1) and (len(success_list) == 0):
                        # Plural fail, no success.
                        replystr = '%s The mod(s) mentioned can\'t be muted... but apparently neither can %s.\n'
                        replystr += 'This seems to be due to: %s'
                        replystr = (replystr % (ctx.author.mention, ment_fail, error_str))

            elif not tried_to_mute_mod:
                if (len(ctx.message.mentions) == 0):
                    # Failed to mention anyone.
                    replystr = '%s You foolish smud, how am I supposed to know who to mute if you fail to mention anyone?'
                    replystr = (replystr % (ctx.author.mention,))

                elif (len(fail_list) == 0) and (len(success_list) == 1):
                    # No fail, singular success.
                    replystr = '%s Fantastic, now we won\'t have to listen to %s for %s.'
                    replystr = (replystr % (ctx.author.mention, ment_success, time_str))

                elif (len(fail_list) == 0) and (len(success_list) > 1):
                    # No fail, plural success.
                    replystr = '%s Absolutely wonderful, %s are smuds whose freedom of speech has been revoked for %s.'
                    replystr = (replystr % (ctx.author.mention, ment_success, time_str))

                elif (len(fail_list) > 0) and (len(success_list) > 0):
                    # At least one fail and at least one success.
                    replystr = '%s Not all people mentioned could be muted. While %s will be shut up for %s, it seems %s will still roam free.\n'
                    replystr += 'The error seems to have been due to: %s'
                    replystr = (replystr % (ctx.author.mention, ment_success, time_str, ment_fail))

                elif (len(fail_list) == 1) and (len(success_list) == 0):
                    # Singular fail, no success.
                    error_str = error_str.lower().replace('.', '')
                    replystr = '%s Excellent decision! ...but nope. Due to %s %s will continue to roam free.'
                    replystr = (replystr % (ctx.author.mention, error_str, ment_fail))

                elif (len(fail_list) > 0) and (len(success_list) == 0):
                    # Plural fail, no success.
                    error_str = error_str.lower().replace('.', '')
                    replystr = '%s Excellent decision! ...but nope. Due to %s %s will continue to roam free.'
                    replystr = (replystr % (ctx.author.mention, error_str, ment_fail))

        await ctx.send(replystr)


    @commands.command(name='unmute', aliases=['unexile', 'unbanish', 'pardon'])
    @commands.check(checks.is_mod)
    async def _unmute(self, ctx, *args):
        # This function deletes the user mute entry from userdb, and removes
        # the mute tag (antarctica tag) from the user.
        antarctica = discord.utils.get(ctx.guild.roles, name='Antarctica')

        # list_mute() gives us lots of info, but we only need to retreieve the member
        # objects of the people muted on the server where the command is issued.
        # Since this is only used by mods the voluntary thing is irrelevant, and
        # since we're forcing removal of the tag the time isn't interesting either.
        felon_list = { discord.utils.get(ctx.guild.members, id=i['user']) for i in userdb.list_mute() if i['server'] == ctx.guild.id }

        # Sometimes a user can be assigned a role manually and thus not end up in the database,
        # and sometimes there may be an error in the database where the user wasn't removed.
        # For this reason we make separate sets of users who are to be removed from the db
        # and users who are gonna have their database entries removed. In most cases
        # these sets are going to be identical.
        remove_from_db = set(ctx.message.mentions).intersection(felon_list)
        remove_role = { user for user in ctx.message.mentions if antarctica in user.roles }

        # We'll start with removing roles since this is the step most likely to
        # generate an error, if there is an error we won't remove them from db.
        # Furthermore not removing them from the db is fairly inconsequential.
        forbidden_error = False
        http_error = False
        success_list = list()
        fail_list = list()
        reason = self.extract_reason(' '.join(args))

        for user in remove_role:
            try:
                if reason == None:
                    await user.remove_roles(antarctica)
                else:
                    await user.remove_roles(antarctica, reason=reason)
                success_list.append(user)

            except discord.Forbidden:
                forbidden_error = True
                remove_from_db.discard(user)
                fail_list.append(user)

            except discord.HTTPException:
                http_error = True
                remove_from_db.discard(user)
                fail_list.append(user)

        # Next up we'll remove them from the db.
        for user in remove_from_db:
            # fix_mute(user, voluntary=False, until=None, delete=False)
            userdb.fix_mute(user, delete=True)

        # Let's explain what went wrong if anything:
        if forbidden_error and not http_error:
            error_str = 'Insufficient privilegies.'

        elif not forbidden_error and http_error:
            error_str = 'HTTP issues.'

        elif forbidden_error and http_error:
            error_str = 'A mix of insufficient privilegies and HTTP issues.'

        # Finally it's time to post some responses.
        ment_success = native.mentions_list(success_list)
        ment_fail = native.mentions_list(fail_list)

        if len(remove_role) == 0:
            # No mentions.
            replystr = '%s You failed to mention anyone muted, twat.'
            replystr = (replystr % (ctx.author.mention,))

        elif (len(success_list) == 1) and (len(fail_list) == 0):
            # Singular success.
            replystr = '%s Don\'t blame me when %s starts causing trouble again. That\'s on you.'
            replystr = (replystr % (ctx.author.mention, ment_success))

        elif (len(success_list) > 1) and (len(fail_list) == 0):
            # Plural success.
            replystr = '%s Just don\'t come crying to me when %s start causing mayhem again, as they most certainly will.'
            replystr = (replystr % (ctx.author.mention, ment_success))

        elif (len(success_list) == 0) and (len(fail_list) == 1):
            # Singular fail.
            replystr = '%s For some reason I wasn\'t able to unmute %s It\'s probably for the best, however this error '
            replystr += 'was likely due to: %s'
            replystr = (replystr % (ctx.author.mention, ment_fail, error_str))

        elif (len(success_list) == 0) and (len(fail_list) > 1):
            # Plural fail.
            ment_fail = ment_fail.replace(' and ', ' or ')
            replystr = '%s We have a crisis on our hands, none of %s could be unmuted. While this is probably for the best, '
            replystr += 'my diagnostics tell me this error has it roots in: %s'
            replystr = (replystr % (ctx.author.mention, ment_fail, error_str))

        else:
            # Mixed results.
            replystr = '%s The operation came back with mixed results, I wasn\'t able to unmute all of the requested users.\n'
            replystr += 'Unmuted: %s\nNot unmuted: %s\n The error(s) seem to have been due to: %s'
            replystr = (replystr % (ctx.author.mention, ment_success, ment_fail, error_str))

        await ctx.send(replystr)


    @commands.command(name='ban', aliases=['purgeban', 'banpurge'])
    @commands.check(checks.is_mod)
    async def _ban(self, ctx, *args):
        # This function simply bans a user from the server in which it's issued.
        reason = self.extract_reason(' '.join(args))
        forbidden_error = False
        http_error = False
        success_list = list()
        fail_list = list()

        if 'list' in args:
            # This is just a shortcut to invoke the listban command.
            banlist = True
        else:
            banlist = False

        if ctx.invoked_with == 'ban':
            do_purge = False
        else:
            do_purge = True

        mod_role = discord.utils.get(ctx.guild.roles, name='Administration')
        mods_list = [ user for user in ctx.message.mentions if mod_role in user.roles ]

        if len(mods_list) > 0:
            tried_to_ban_mod = True
        else:
            tried_to_ban_mod = False

        for victim in [ user for user in ctx.message.mentions if user not in mods_list]:
            try:
                if not do_purge:
                    await ctx.guild.ban(victim, reason=reason, delete_message_days=0)
                else:
                    await ctx.guild.ban(victim, reason=reason, delete_message_days=7)

                success_list.append(victim)

            except discord.Forbidden:
                forbidden_error = True
                fail_list.append(victim)

            except discord.HTTPException:
                http_error = True
                fail_list.append(victim)

        # And now we compile a response.
        ment_success = native.mentions_list(success_list)
        ment_fail = native.mentions_list(fail_list)

        # Error list:
        if forbidden_error and not http_error:
            error_str = 'Insufficient privilegies.'
        elif not forbidden_error and http_error:
            error_str = 'HTTP issues.'
        else:
            error_str = 'A mix of insufficient privilegies and HTTP issues.'

        if banlist:
            # This is just a shortcut to invoke the listban command.
            await ctx.invoke(self.bot.get_command('listban'))

        elif len(ctx.message.mentions) == 0:
            # No mentions
            replystr = 'Sure, I\'ll go right ahead and ban... wait who should I ban? You didn\'t mention anyone? Freeze in hell %s!'
            replystr = (replystr % (ctx.author.mention,))

        elif len(ctx.message.mentions) == len(mods_list):
            # No mentions that weren't mods
            replystr = '%s Every single person on that list of yours is a mod. This is mutiny!'
            replystr = (replystr % (ctx.author.mention,))

        elif (len(success_list) == 1) and (len(fail_list) == 0):
            # Singular success
            replystr = '%s The smuddy little smud %s won\'t bother us no more, if you know what I mean... :hammer:'
            replystr = (replystr % (ctx.author.mention, ment_success))

        elif (len(success_list) > 1) and (len(fail_list) == 0):
            # Plural success
            ban_hammer = (':hammer:' * len(success_list))
            replystr = '%s Those smuddy little smuds %s won\'t bother us no more. Because they\'re all BANNED! %s'
            replystr = (replystr % (ctx.author.mention, ment_success, ban_hammer))

        elif (len(success_list) > 0) and (len(fail_list) > 0):
            # Mixed results
            error_str = error_str.lower().replace('.', '').replace('http', 'HTTP')
            replystr = '%s My powers are disapating, due to %s I wasn\'t able to ban all of the users requested.'
            replystr += '\nBanned: %s\nNot banned: %s'
            replystr = (replystr % (ctx.author.mention, error_str, ment_success, ment_fail))

        elif (len(success_list) == 0) and (len(fail_list) == 1):
            # Singular fail
            error_str = error_str.lower().replace('.', '').replace('http', 'HTTP')
            replystr = '%s The smuddy little smud %s... will actually keep bothering us. I wasn\'t able to ban them due to %s.'
            replystr = (replystr % (ctx.author.mention, ment_fail, error_str))

        elif (len(success_list) == 0) and (len(fail_list) > 1):
            # Plural fail
            ment_fail = ment_fail.replace(' and ', ' or ')
            replystr = '%s I\'m deeply ashamed to say that my systems are malfunctioning and I wasn\'t able to ban %s.\n'
            replystr += 'This seems to be due to: %s'
            replystr = (replystr % (ctx.author.mention, ment_fail, error_str))

        if not banlist:
            await ctx.send(replystr)


    @commands.command(name='unban')
    @commands.check(checks.is_mod)
    async def _unban(self, ctx, *args):
        # This function simply remover the ban of a user from the server in which it's issued.
        forbidden_error = False
        http_error = False
        banlist = list()

        # This is a shortcut to invoke the banlist command with !unban list.
        if args == ('list',):
            showbans = True
        else:
            showbans = False

        try:
            banlist = await ctx.guild.bans()
        except discord.Forbidden:
            forbidden_error = True
        except discord.HTTPException:
            http_error = True

        # We will assume that all args that are digits are ids
        # and all args of the form characters#fourdigits are
        # user names.
        usr_names = re.findall('(?<=\s)\S+#\d{4}(?=\s)', (' ' + ctx.message.content + ' '))
        usr_ids = re.findall('(?<=\s)\d+(?=\s)', (' ' + ctx.message.content + ' '))

        success_list = list()
        fail_list = list()
        found_anyone = False
        for ban_entry in banlist:
            user = ban_entry.user
            user_str = ('%s#%s' % (user.name, str(user.discriminator)))

            # Below is an easy and expandable way to add criterias for unbanning.
            # Every if-statement corresponds to one criteria.
            #
            # For example we could easily add this as an extra criteria if we wanted to.
            # This would match any username, not requiring the #identifier
            # elif (' ' + user.name + ' ') in (' ' + ctx.message.content + ' '):
            #     entry_hit = True

            if user_str in usr_names:
                entry_hit = True
            elif (str(user.id) in usr_ids):
                entry_hit = True
            else:
                entry_hit = False

            # If any of the above resulted in a hit, we'll try to remove the ban.
            if entry_hit:
                found_anyone = True
                try:
                    await ctx.guild.unban(user)
                    success_list.append(user)

                except discord.Forbidden:
                    forbidden_error = True
                    fail_list.append(user)

                except discord.HTTPException:
                    http_error = True
                    fail_list.append(user)

        if forbidden_error or http_error:
            any_error = True
        else:
            any_error = False

        if forbidden_error and http_error:
            error_str = 'a mix of insufficient privilegies and HTTP issues'
        elif forbidden_error:
            error_str = 'insufficient privilegies'
        elif http_error:
            error_str = 'HTTP issues'
        else:
            error_str = 'no errors? (why are you seeing this?)'

        # Now all we need is a reply string.
        ment_success = native.mentions_list(success_list)
        ment_fail = native.mentions_list(fail_list)


        if showbans:
            # This is just a shortcut to invoke the listban command.
            await ctx.invoke(self.bot.get_command('listban'))

        elif not found_anyone and not any_error:
            # No banned users were found in the message.
            replystr = '%s I wasn\'t able to spot any banned usernames or IDs in that message of yours.'
            replystr = (replystr % (ctx.author.mention,))

        elif any_error and len(fail_list) == 0:
            # Encountered an error during listing,
            # no unban attempts have been made.
            replystr = '%s Due to %s I wasn\'t able to retrieve the list of banned users. '
            replystr += 'Without that list I can\'t even try to unban them.'
            replystr = (replystr % (ctx.author.mention, error_str))

        elif len(success_list) == 1 and len(fail_list) == 0:
            # Singular success, no fails.
            replystr = '%s Smuddy Mc Smudface AKA %s has been unbanned, happy now?'
            replystr = (replystr % (ctx.author.mention, ment_success))

        elif len(success_list) > 1 and len(fail_list) == 0:
            # Plural success, no fails.
            replystr = '%s The users known as %s have been unbanned... but why?'
            replystr = (replystr % (ctx.author.mention, ment_success))

        elif len(success_list) > 0 and len(fail_list) > 0:
            # Mixed results.
            replystr = '%s The unbanning was a success! Partially anyway...\n'
            replystr += 'Unbanned user(s): %s\n'
            replystr += 'Still banned user(s): %s'
            replystr += 'Failure was caused by %s.'
            replystr = (replystr % (ctx.author.mention, ment_success, ment_fail, error_str))

        elif len(success_list) == 0 and len(fail_list) == 1:
            # No success, singular fail.
            replystr = '%s I wasn\'t able to unban %s due to %s.'
            replystr = (replystr % (ctx.author.mention, ment_fail, error_str))

        elif len(success_list) == 0 and len(fail_list) > 1:
            # No success, plural fails.
            ment_fail = ment_fail.replace(' and ', ' or ')
            replystr = '%s I wasn\'t able to unban %s due to %s.'
            replystr = (replystr % (ctx.author.mention, ment_fail, error_str))

        else:
            replystr = '%s Someone call <@!154516898434908160>! I don\'t know what\'s going on!!!\n'
            replystr += 'len(success_list) == %s, len(fail_list) == %s\n'
            replystr += 'http_error == %s, forbidden_error == %s'
            replystr = (replystr % (ctx.author.mention, str(len(success_list))), str(len(fail_list)), str(http_error), str(forbidden_error))

        if not showbans:
            await ctx.send(replystr)



    @commands.command(name='listban', aliases=['banlist','listbans','banslist'])
    @commands.check(checks.is_mod)
    async def _listban(self, ctx):
        # Because it's tricky to find the exact user name/id when you can't highlight people,
        # this function exists to get easy access to the list of bans in order to unban.

        # Viewing list of bans requires mod permissions.
        forbidden_error = False
        http_error = False

        try:
            banlist = await ctx.guild.bans()
        except discord.Forbidden:
            forbidden_error = True
        except discord.HTTPException:
            http_error = True

        general_error = (forbidden_error or http_error)

        if forbidden_error and not http_error:
            error_str = 'insufficient privilegies'
        elif not forbidden_error and http_error:
            error_str = 'HTTP issues'
        else:
            # This shouldn't happen, but you can never be too sure.
            error_str = 'a mix of insufficient privilegies and HTTP issues'

        if not general_error:
            if len(banlist) == 0:
                replystr = '%s There are no banned users... yet. If you\'d like to change that just say the word!'
                replystr = (replystr % (ctx.author.mention,))

            else:
                replystr = 'The following users are currently banned:\n'
                for ban in banlist:
                    if ban.reason == None:
                        add_str = '**%s#%s** (id: %s)'
                        add_str = (add_str % (ban.user.name, str(ban.user.discriminator), str(ban.user.id)))

                    else:
                        add_str = '**%s#%s** (id: %s)\n(%s was banned for: %s)'
                        add_str = (add_str % (ban.user.name, str(ban.user.discriminator), str(ban.user.id), ban.user.name, ban.reason))

                    if ban != banlist[-1]:
                        add_str += '\n'
                    replystr += add_str
        else:
            replystr = '%s Due to %s I wasn\'t able to retrieve the list of banned smuds.'
            replystr = (replystr % (ctx.author.mention, error_str,))

        await ctx.send(replystr)


    @commands.command(name='kick')
    @commands.check(checks.is_mod)
    async def _kick(self, ctx, *args):
        # This function kicks the user out of the server in which it is issued.
        success_list = list()
        fail_list = list()
        mods_list = list()
        forbidden_error = False
        http_error = False
        reason = self.extract_reason(' '.join(args))

        # If they tried to kick a mod christmas is cancelled.
        mod_role = discord.utils.get(ctx.guild.roles, name='Administration')
        mods_list = [ user for user in ctx.message.mentions if mod_role in user.roles ]
        ment_mods = native.mentions_list(mods_list)
        if len(mods_list) == 0:
            tried_to_kick_mod = False
        else:
            tried_to_kick_mod = True

        # Start the kicking.
        if len(ctx.message.mentions) > 0 and not tried_to_kick_mod:
            for victim in ctx.message.mentions:
                try:
                    if reason == None:
                        await ctx.guild.kick(victim)
                    else:
                        await ctx.guild.kick(victim, reason=reason)
                    success_list.append(victim)

                except discord.Forbidden:
                    fail_list.append(victim)
                    forbidden_error = True

                except discord.HTTPException:
                    fail_list.append(victim)
                    http_error = True

        # This will convert the lists into mentions suitable for text display:
        # user1, user2 and user 3
        ment_success = native.mentions_list(success_list)
        ment_fail = native.mentions_list(fail_list)


        ### Preparation of replystrings.
        ### Errors are added further down.

        # Had at least one success and no fails.
        if (len(success_list) > 0) and (len(fail_list) == 0):

            # Singular
            if len(success_list) == 1:
                replystr = '%s The smud who goes by the name of %s has been kicked from the server, never to be seen again!'
                replystr = (replystr % (ctx.author.mention, ment_success))

            # Plural
            else:
                replystr = '%s The smuds who go by the names of %s have been kicked from the server, never to be seen again!'
                replystr = (replystr % (ctx.author.mention, ment_success))

        # Had no successes and at least one fail.
        elif (len(success_list) == 0) and (len(fail_list) > 0):

            # Singular
            if len(fail_list) == 1:
                replystr = '%s So... it seems I wasn\'t able to kick %s due to: '
                replystr = (replystr % (ctx.author.mention, ment_fail))

            # Plural
            else:
                replystr = '%s So... it seems I wasn\'t able to kick any of %s.\nThis was due to: '
                replystr = (replystr % (ctx.author.mention, ment_fail))

        # Had at least one success and at least one fail.
        elif (len(success_list) > 0) and (len(fail_list) > 0):
            # Singular and plural don't matter here.
            replystr = '%s The request was executed with mixed results.\nKicked: %s\nNot kicked: %s\nThis was due to: '
            replystr = (replystr % (ctx.author.mention, ment_success, ment_fail))

        # Had no mentions whatsoever.
        elif len(ctx.message.mentions) == 0:
            # Singular and plural don't matter here.
            replystr = '%s You forgot to mention anyone you doofus. Who exactly am I meant to kick??'
            replystr = (replystr % (ctx.author.mention,))

        ### Now we're adding in the error codes if there are any.
        if forbidden_error and http_error:
            replystr += 'Insufficient privilegies and HTTP exception.'
        elif not forbidden_error and http_error:
            replystr += 'HTTP exception.'
        elif forbidden_error and not http_error:
            replystr += 'Insufficient privilegies.'

        ### Finally, a special message to people who tried to kick a mod.
        if tried_to_kick_mod:
            if (len(mods_list) == 1) and ctx.author in mods_list:
                replystr = '%s You can\'t kick yourself, silly.'
                replystr = (replystr % (ctx.author.mention))
            else:
                replystr = '%s Not even you can kick the likes of %s.'
                replystr = (replystr % (ctx.author.mention, ment_mods))

        await ctx.send(replystr)


    @commands.command(name='purge', aliases=['clean', 'cleanup'])
    @commands.check(checks.is_mod)
    async def _purge(self, ctx, *args):
        # This function will remove the last X number of posts in the channel.
        #
        # Features:
        # - If message contains mentions, it will only delete messages by
        #   the people mentioned.
        # - Limit is 100 messages.
        # - Delets message which called the function.
        try:
            await ctx.message.delete()
        except:
            pass

        # We'll use the first number we can find in the arguments.
        delete_no = 0
        for arg in args:
            if arg.isdigit() and delete_no == 0:
                delete_no = int(arg)

        if delete_no < 0:
            delete_no = 0
        elif delete_no > 100:
            delete_no = 100

        def check_func(message):
            # Author in mentions    True
            # No mentions           True
            # -> Otherwise          False
            if message.author in ctx.message.mentions:
                return True
            elif len(ctx.message.mentions) == 0:
                return True
            else:
                return False

        try:
            await ctx.channel.purge(limit=delete_no, check=check_func)

        except discord.Forbidden:
            replystr = '%s An error occured, it seems I\'m lacking the privilegies '
            replystr += 'to carry out your Great Purge.'
            replystr = (replystr % (ctx.author.mention,))
            await ctx.send(replystr)

        except discord.HTTPException:
            replystr = '%s An error occured, it seems my HTTP sockets are glitching out '
            replystr += 'and thus couldn\'t carry out your Great Purge.'
            replystr = (replystr % (ctx.author.mention,))
            await ctx.send(replystr)

        except:
            replystr = '%s Something went wrong with your Great Purge and I don\'t '
            replystr += 'really know what. It\'s not related to HTTP or permissions...'
            await ctx.send(replystr)

def setup(bot):
    bot.add_cog(ModCmdsCog(bot))
