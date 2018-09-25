import discord, re, datetime
from discord.ext import commands
from botfunctions import checks, native, userdb

# This cog is for commands restricted to mods on a server.
# It features commands such as !ban, !mute, etc.

class ModCmdsCog:
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
        tried_to_mute_mod = False
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
            add_time = datetime.timedelta(seconds=30)
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
        for victim in ctx.message.mentions:
            if await checks.is_mod(victim):
                tried_to_mute_mod = True
                mods_list.append(victim)
        ment_mods = native.mentions_list(mods_list)

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
            error_str = 'HTTP troubles.'
        else:
            error_str = 'A mix of insufficient privilegies and HTTP troubles.'

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


    @commands.command(name='unmute', aliases=['unexile', 'unbanish'])
    @commands.check(checks.is_mod)
    async def _unmute(self, ctx):
        # This function deletes the user mute entry from userdb, and removes
        # the mute tag (antarctica tag) from the user.
        pass

    @commands.command(name='ban')
    @commands.check(checks.is_mod)
    async def _ban(self, ctx):
        # This function simply bans a user from the server in which it's issued.
        pass

    @commands.command(name='unban')
    @commands.check(checks.is_mod)
    async def _unban(self, ctx):
        # This function simply remover the ban of a user from the server in which it's issued.
        pass

    @commands.command(name='listban')
    @commands.check(checks.is_mod)
    async def _unban(self, ctx):
        # Because it's tricky to find the exact user name/id when you can't highlight people,
        # this function exists to get easy access to the list of bans in order to unban.
        pass

    @commands.command(name='kick')
    @commands.check(checks.is_mod)
    async def _kick(self, ctx, *args):
        # This function kicks the user out of the server in which it is issued.
        success_list = list()
        fail_list = list()
        mods_list = list()
        forbidden_error = False
        http_error = False
        tried_to_kick_mod = False
        reason = self.extract_reason(' '.join(args))
        ### TODO: Enter the reason into the kick command.

        # If they tried to kick a mod christmas is cancelled.
        for victim in ctx.message.mentions:
            if await checks.is_mod(victim):
                tried_to_kick_mod = True
                mods_list.append(victim)
        ment_mods = native.mentions_list(mods_list)

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
        # This function will remove the last X number of posts.
        # Specifying a negative number or 0 won't do anything.
        # It will also delete the !purge-message, i.e. the number specified + 1.
        # It has a limit of 100 messages.
        number = 0

        try:
            number += int(args[0])
        except:
            pass

        # Deleting the requested number of messages AND the !purge message.
        number += 1

        # We will never delete more than 100 messages.
        if number > 100:
            number == 100

        if (number > 1):
            await ctx.channel.purge(limit=number)

def setup(bot):
    bot.add_cog(ModCmdsCog(bot))
