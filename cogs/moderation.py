import discord, re, datetime, asyncio
from discord.ext import commands
from internals import native, checks, var, templates
from databases import mutes

# This cog is for commands restricted to mods on a server.
# It features commands such as !ban, !mute, etc.

class ModCmdsCog(commands.Cog, name='Moderation'):
    """Good mod! Read the manual! Or if you're not mod - sod off!"""
    def __init__(self, bot):
        self.bot = bot
        self.antarctica_role    = dict()
        self.antarctica_channel = dict()
        self.trash_channel      = dict()
        self.banish_templates   = templates.banish_templates()

        bot.add_bg_task(self.unbanish_loop(), 'unbanish loop')
        self.unbanish_interval = 20

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.antarctica_role[guild.id]      = native.get_antarctica_role(guild)
            self.antarctica_channel[guild.id]   = native.get_antarctica_channel(guild)
            self.trash_channel[guild.id]        = native.get_trash_channel(guild)

    def check_roles(self, role):
        """When roles are created/deleted/updated this function checks that this
        doesn't affect which role is antarctica."""
        guild = role.guild

        old_antarctica = self.antarctica_role[guild.id]
        new_antarctica = native.get_antarctica_role(guild)

        if old_antarctica != new_antarctica:
            self.antarctica_role[guild.id] = new_antarctica
            if new_antarctica != None:  new_antarctica = f"{var.green}@{new_antarctica}"
            else:                       new_antarctica = f"{var.red}undefined"
            print(f"{var.cyan}The {var.boldwhite}Antarctica role{var.cyan} in",
                  f"{var.red}{guild.name}{var.cyan} was updated to: {new_antarctica}{var.reset}")

    def check_channels(self, channel):
        """When channels are created/deleted/updated this function checks that this
        doesn't affect which channel is bot-trash, antarctica, etc."""
        guild = channel.guild

        # Check if antarctica has changed.
        old_antarctica  = self.antarctica_channel[guild.id]
        new_antarctica  = native.get_antarctica_channel(guild)

        if old_antarctica != new_antarctica:
            self.antarctica_channel[guild.id] = new_antarctica

            if new_antarctica != None:  new_antarctica = f"{var.green}#{new_antarctica.name}{var.reset}"
            else:                       new_antarctica = f"{var.red}undefined"

            print(f"{var.cyan}The {var.boldwhite}Antarctica channel{var.cyan} in",
                  f"{var.red}{guild.name}{var.cyan} was updated to: {new_antarctica}{var.reset}")

        # Check if trash has changed.
        old_trash       = self.trash_channel[guild.id]
        new_trash       = native.get_trash_channel(guild)

        if old_trash != new_trash:
            self.trash_channel[guild.id] = new_trash

            if new_trash != None:   new_trash = f"{var.green}#{new_trash.name}"
            else:                   new_trash = f"{var.red}undefined"

            print(f"{var.cyan}The {var.boldwhite}trash channel{var.cyan} in",
                  f"{var.red}{guild.name}{var.cyan} was updated to: {new_trash}{var.reset}")

    # Run check_channels() and check_roles() when a channel/role is updated somewhere.
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):       self.check_channels(channel)
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):       self.check_channels(channel)
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after): self.check_channels(after)
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):             self.check_roles(role)
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):             self.check_roles(role)
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):    self.check_roles(after)

    async def unbanish_loop(self):
        """This loop checks for people to unbanish every self.banish_interval seconds."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            # The unbanish interval can potentially be changed through settings.
            await asyncio.sleep(self.unbanish_interval)

            for server in self.bot.guilds:
                banishes = [ user for user in mutes.list_server(server) if user['due'] == True ]

                # If no unbanishes due, continue to next server.
                # If there are, get the antarctica role for current server.
                if len(banishes) == 0:
                    continue
                else:
                    antarctica = self.antarctica_role[server.id]
                    channel = self.antarctica_channel[server.id]

                # Sequentially remove users from mute database, then remove antarctacia role.
                # If both of these steps succeeded add them to success_list so we can mention them later.
                success_list = list()
                for user in banishes:
                    user = server.get_member(user['user'])
                    try:
                        mutes.remove(user)
                        if antarctica in user.roles:
                            await user.remove_roles(antarctica)
                            success_list.append(user)
                    except Exception as e:
                        print(f"{var.red}ERROR {var.cyan} Failed to remove {var.red}@{antarctica.name} {var.cyan}from" +
                            f"{var.boldwhite}{user.name}#{user.discriminator} {var.cyan}in {var.red}{server.name}.")

                # Post success message to the server's designated Antarctica channel.
                if len(success_list) != 0:
                    ment_success = native.mentions_list(success_list)
                    await channel.send(f"It's with great regret that I must inform you all that {ment_success}'s exile has come to an end.")

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
        if len(output.strip()) == 0:    return None
        else:                           return output.strip()


    @commands.command(name='say', aliases=['speak', 'chat'])
    @commands.check(checks.is_mod)
    async def _say(self, ctx, channel : discord.TextChannel, *args):
        """Let me be your voice!"""
        replystr = ' '.join(args)

        # Now let's find all the custom emoji to make sure they all work.
        # If any of them don't, halt operations.
        emoji = re.findall('<a?:\w+:(\d+)(?=>)', replystr)
        impossible = False
        for i in emoji:
            if self.bot.get_emoji(int(i)) == None:
                impossible = True
                break

        # If a string of numbers is found, see if it's a user ID.
        # 1. Find strings of numbers not belonging to a mention.
        # 2. See if that number is a user ID for anyone we know.
        users = re.findall('(?:\s|^)(\d+)', replystr)
        users = [ ctx.guild.get_member(int(user)) for user in users if ctx.guild.get_member(int(user)) != None ]
        for user in users:
            replystr = replystr.replace(str(user.id), user.mention)
            replystr = replystr.replace(f'<@!<@!{user.id}>>', user.mention)

        if impossible:  await ctx.channel.send(f"{ctx.author.mention} Abort! Abort! There are emoji in your message that I can't use..")
        else:           await channel.send(replystr)


    @commands.command(name='rules', aliases=['rule'])
    async def _rules(self, ctx, *args):
        """Remind users of what the rules are."""
        rules = {
            1: "Rule 1: Be nice and decent to everyone. Hate speech will not be tolerated.",
            2: "Rule 2: Keep discussions civil and mature.",
            3: "Rule 3: Stay on topic and avoid spamming.",
        }

        rule_triggers = {
            1: ('1', 'joke', 'jokes', 'joking', 'sex', 'sexual', 'weight', 'race', 'skin',
                'color', 'colour', 'gender', 'nice', 'decent', 'hate'),
            2: ('2', 'civil', 'civility', 'mature', 'maturity', 'disagreement', 'dismissive',
                'dismissal', 'opinion', 'opinions', 'shoe', 'shoes', 'shoesize', 'age', 'act',
                'behave'),
            3: ('3', 'topic', 'ontopic', 'offtopic', 'spam', 'nonsense')
        }

        request = ' '.join(args).lower()
        called_rules = str()

        if 'all' in request:
            for rule in rules:
                called_rules += f"{rules[rule]}\n"
        else:
            for rule in rule_triggers:
                for keyword in rule_triggers[rule]:
                    if keyword in request and str(rule) not in called_rules:
                        called_rules += f"{rules[rule]}\n"

        if len(called_rules) == 0:  await ctx.send(f"Sorry {ctx.author.mention}, your terms don't seem to match any rules. :thinking:")
        else:                       await ctx.send(called_rules.strip())


    @commands.command(name='mute', aliases=[ 'pardon', 'forgive',
        'banish', 'unbanish', 'microbanish', 'superbanish', 'SUPERBANISH', 'megabanish', 'MEGABANISH',
        'hogtie', 'unhogtie', 'microhogtie', 'superhogtie', 'SUPERHOGTIE', 'megahogtie', 'MEGAHOGTIE',
                  'unmute',   'micromute',   'supermute',   'SUPERMUTE',   'megamute',   'MEGAMUTE',
    ])
    @commands.check(checks.is_mod)
    async def _banish(self, ctx, *args):
        """Restrict a user to #antarctica for a short(?) period of time or frees them from that hell."""

        # This function is carried out through the following subfunctions:
        # muteparse(context, arguments)     Parse the command.
        # mutecount()                       Count number of mutes.
        # mutecheck()                       Check if one or more users are already muted.
        # muteadd()                         Mute one or more users.
        # muteremove()                      Unmute one or more users

        async def muteparse(context, arguments):
            """Uses context and arguments to determine what is to be done.
            Returns a dictionary with information for what the rest of the function should do.

            It outputs a dictionary with the following data:
                { 'command':     string with command category (mute or unmute)
                  'flavor':      if applicable the flavor or the command, subcommand if you will. otherwise None.
                  'mods':        list item with all, if any, mods that were mentioned.
                  'users':       list item with all, if any, non-mod/bot/author users that were mentioned.
                  'self':        True if ctx.author was mentioned, otherwise None.
                  'time':        datetime object if micro or super commands were used, otherwise None.
                  'duration':    specifies how long the mute is in words
                  'server':      the guild object
                }"""

            # Initialize the dict we're going to return.
            mission = {
            'command'  : None,
            'flavor'   : None,
            'mods'     : list(),
            'users'    : list(),
            'self'     : (context.author in context.message.mentions),
            'mrfreeze' : (self.bot.user in context.message.mentions),
            'time'     : None,
            'duration' : str(),
            'server'   : context.guild
            }

            # Command categories:
            # check             Checks if user or users are banished.
            # count             Check how many users are in the banish DB
            # mute              Adds the Antarctica role to a user.
            # unmute            Removes the Antarctica role from a user.
            # Command flavors:  mute, banish
            if 'banish' in context.invoked_with.lower():    mission['flavor'] = 'banish'
            elif 'hogtie' in context.invoked_with.lower():  mission['flavor'] = 'hogtie'
            else:                                           mission['flavor'] = 'mute'

            mute_aliases = (
                'banish', 'microbanish', 'superbanish', 'SUPERBANISH', 'megabanish', 'MEGABANISH',
                'hogtie', 'microhogtie', 'superhogtie', 'SUPERHOGTIE', 'megahogtie', 'MEGAHOGTIE',
                'mute',   'micromute',   'supermute',   'SUPERMUTE',   'megamute',   'MEGAMUTE',
            )
            unmute_aliases = (
                'unbanish', 'unhogtie', 'unmute', 'pardon', 'forgive',
            )

            if 'check' in arguments:    mission['command'] = 'check'
            elif 'count' in arguments:  mission['command'] = 'count'
            elif context.invoked_with in mute_aliases:
                mission['command'] = 'mute'
                if 'micro' in context.invoked_with:
                    mission['time'] = datetime.datetime.now()
                    mission['duration'] = 'only about a minute'

                elif 'super' in context.invoked_with.lower():
                    nextyear = datetime.datetime.now().year + 1
                    mission['time'] = datetime.datetime.now().replace(year=nextyear)
                    mission['duration'] = 'ONE FULL YEAR'

                elif 'mega' in context.invoked_with.lower():
                    nextyear = datetime.datetime.now().year + 1000
                    mission['time'] = datetime.datetime.now().replace(year=nextyear)
                    mission['duration'] = 'A MILLENIUM'

            elif context.invoked_with in unmute_aliases:
                mission['command'] = 'unmute'

            # Mention categories: mods, bots, users
            for mention in context.message.mentions:
                if mention == self.bot.user:        pass # Don't banish the bot.
                elif await checks.is_mod(mention):  mission['mods'].append(mention)
                else:                               mission['users'].append(mention)

            return mission


        async def mutecount(mission):
            """Counts the number of users muted on this server."""
            result = mutes.count(mission['server'])
            verb = self.banish_templates[mission['flavor']]['past_tense']
            if result == 0:     await ctx.send(f"{ctx.author.mention} There is no one {verb} here. Fix it!")
            elif result == 1:   await ctx.send(f"{ctx.author.mention} There is only a single person {verb} here. Who could it be??")
            else:               await ctx.send(f"{ctx.author.mention} There are {result} people {verb} here. As it should be.")


        async def mutecheck(mission):
            """Checks if one or more users are muted/banished."""
            if len(ctx.message.mentions) == 0:
                await ctx.send(f"{ctx.author.mention} You didn't mention anyone you smud.")
            else:
                verb = self.banish_templates[mission['flavor']]['past_tense']
                reply = str()

                for user in ctx.message.mentions:
                    checkresult = mutes.check(user)
                    if isinstance(checkresult, bool):
                        if checkresult: reply += f"{user.mention} is {verb} for life.\n"
                        else:           reply += f"{user.mention} is not {verb}.\n"

                    elif isinstance(checkresult, datetime.datetime):
                        until = native.parse_timedelta(checkresult - datetime.datetime.now())
                        reply += f"{user.mention} is going to be {verb} for another {until}.\n"

                    else:
                        reply += f"I'm not sure about {user.mention} actually. :shrug:\n"

                await ctx.send(reply)


        async def muteadd(mission):
            """Adds one or more users to the mute database and assigns them the antarctica role"""
            antarctica  = self.antarctica_role[mission['server'].id]
            verb        = self.banish_templates[mission['flavor']]['past_tense']
            unmuteables = mission['mods']
            muteables   = mission['users']
            mute_status = { 'new': list(), 'prolonged': list(), 'failed': list() }

            # Default times for various themes are as follows.
            if mission['time'] == None and mission['flavor'] == 'banish':
                mission['time'] = datetime.datetime.now() + datetime.timedelta(minutes=5)
            elif mission['time'] == None and mission['flavor'] == 'hogtie':
                mission['time'] = datetime.datetime.now() + datetime.timedelta(minutes=10)

            for victim in muteables:
                # 1. Always add the Antarctica role if the user doesn't have it.
                # 2. If the user both have the role and are in the database, this is a prolonged mute.
                # -> If a user has the role removed they should've been removed from the database. This is a failsafe.

                has_role = antarctica in victim.roles
                in_db    = mutes.check(victim) != False
                prolong  = has_role and in_db
                if not has_role:
                    try:                    await victim.add_roles(antarctica, reason=f"!{verb} by {ctx.author.name}")
                    except Exception as e:  mute_status['failed'].append([victim, e])

                if prolong:     mutes.prolong(victim, voluntary=False, end_date=mission['time'])
                else:               mutes.add(victim, voluntary=False, end_date=mission['time'])

            # Responses...
            responses = self.banish_templates[mission['flavor']]
            reply = None

            # Set variables success_list, fail_list and errors for later on.
            success_list = native.mentions_list(mute_status['new'] + mute_status['prolonged'])
            fail_list = native.mentions_list( [ fail[0] for fail in mute_status['failed'] ] )

            if len(fail_list) != 0:
                errors = ', '.join( [ fail[1] for fail in mute_status['failed'] ] )
            else:
                errors = "No errors!"

            if len(muteables) == 0:
                #####################################################
                # NON-ACTIONABLE REQUESTS (only mods/mrfreeze/self) #
                #####################################################
                if len(ctx.message.mentions) == 1 and mission['self']:
                    reply = responses['selfmute']
                elif mission['mrfreeze']:
                    if len(unmuteables) != 0:
                        if mission['self']:     reply = responses['selfmute']
                        else:                   reply = responses['modfreezemute']
                    elif len(unmuteables) == 0: reply = responses['freezemute']
                elif len(unmuteables) == 1:     reply = responses['singlemodmute']
                elif len(unmuteables) > 1:      reply = responses['multimodmute']

            else:
                ################################################
                # RESPONESE FOR ACTIONABLE REQUESTS START HERE #
                ################################################
                pass

            if reply == None:
                print(f"{var.red}!mute {var.cyan}FAILED to find an appropriate template.{var.reset}")
                await ctx.send("I'm supposed to say something now, but I'm at a loss for words.")
            else:
                reply = reply.substitute(
                    author = ctx.author.mention,
                    victim = success_list,
                    fail = fail_list,
                    error = errors,)
                await ctx.send(reply)

        async def muteremove(mission):
            antarctica = native.get_antarctica_role(mission['server'])

        # Ready to parse the command and determine what is to be done.
        mission = await muteparse(ctx, args)
        if mission['command'] == 'mute' and mission['time'] == None:
            add_time, end_time = native.extract_time(args)
            mission['time'] = end_time
            mission['duration'] = native.parse_timedelta(add_time)

        if mission['command'] == 'count':       await mutecount(mission)
        elif mission['command'] == 'check':     await mutecheck(mission)
        elif mission['command'] == 'mute':      await muteadd(mission)
        elif mission['command'] == 'unmute':    await muteremove(mission)

    @commands.command(name='ban', aliases=['purgeban', 'banpurge'])
    @commands.check(checks.is_mod)
    async def _ban(self, ctx, *args):
        """Remove a user from our sight - permanently."""
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
        """Unpermanent removal from sight of a previously banned user."""
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
            replystr = '%s Smuddy McSmudface, I mean %s, has been unbanned... for some reason. :shrug:'
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
        """Get a list of all banned users (useful for unbanning)."""
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
        """Force a user to leave the server temporarily."""
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

        if len(mods_list) == 0: tried_to_kick_mod = False
        else:                   tried_to_kick_mod = True


        # Start the kicking.
        if len(ctx.message.mentions) > 0 and not tried_to_kick_mod:
            for victim in ctx.message.mentions:
                try:
                    if reason == None:
                        await ctx.guild.kick(victim)
                        print(f"{var.boldwhite}{victim.name}#{victim.discriminator}{var.cyan} was " +
                            f"{var.red} kicked from {ctx.guild.name} {var.cyan}by {var.green}" +
                            f"{ctx.author.name}#{ctx.author.discriminator}")
                    else:
                        await ctx.guild.kick(victim, reason=reason)
                        print(f"{var.boldwhite}{victim.name}#{victim.discriminator}{var.cyan} was " +
                            f"{var.red}kicked from {ctx.guild.name} {var.cyan}by {var.green}" +
                            f"{ctx.author.name}#{ctx.author.discriminator}{var.cyan}.\n{var.boldwhite}Reason given: " +
                            f"{var.white}{reason}{var.reset}")
                    success_list.append(victim)

                except discord.Forbidden:
                    fail_list.append(victim)
                    forbidden_error = True
                    print(f"{var.red}ERROR {var.cyan}I was not allowed to {var.red}!kick {var.boldwhite}{victim.name}#{victim.discriminator}" +
                        f"{var.cyan} in {var.red}{ctx.guild.name}{var.cyan}.{var.reset}")

                except discord.HTTPException:
                    fail_list.append(victim)
                    http_error = True
                    print(f"{var.red}ERROR {var.cyan}I couldn't {var.red}!kick {var.boldwhite}{victim.name}#{victim.discriminator}" +
                        f"{var.cyan} in {var.red}{ctx.guild.name} {var.cyan}due to an HTTP Exception.{var.reset}")

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
                replystr = "%s The smud who goes by the name of %s has been kicked from the server, never to be seen again!"
                replystr = (replystr % (ctx.author.mention, ment_success))

            # Plural
            else:
                replystr = "%s The smuds who go by the names of %s have been kicked from the server, never to be seen again!"
                replystr = (replystr % (ctx.author.mention, ment_success))

        # Had no successes and at least one fail.
        elif (len(success_list) == 0) and (len(fail_list) > 0):

            # Singular
            if len(fail_list) == 1:
                replystr = "%s So... it seems I wasn\'t able to kick %s due to: "
                replystr = (replystr % (ctx.author.mention, ment_fail))

            # Plural
            else:
                replystr = "%s So... it seems I wasn\'t able to kick any of %s.\nThis was due to: "
                replystr = (replystr % (ctx.author.mention, ment_fail))

        # Had at least one success and at least one fail.
        elif (len(success_list) > 0) and (len(fail_list) > 0):
            # Singular and plural don't matter here.
            replystr = "%s The request was executed with mixed results.\nKicked: %s\nNot kicked: %s\nThis was due to: "
            replystr = (replystr % (ctx.author.mention, ment_success, ment_fail))

        # Had no mentions whatsoever.
        elif len(ctx.message.mentions) == 0:
            # Singular and plural don't matter here.
            replystr = "%s You forgot to mention anyone you doofus. Who exactly am I meant to kick??"
            replystr = (replystr % (ctx.author.mention,))

        ### Now we're adding in the error codes if there are any.
        if forbidden_error and http_error:
            replystr += "Insufficient privilegies and HTTP exception."
        elif not forbidden_error and http_error:
            replystr += "HTTP exception."
        elif forbidden_error and not http_error:
            replystr += "Insufficient privilegies."

        ### Finally, a special message to people who tried to kick a mod.
        if tried_to_kick_mod:
            if (len(mods_list) == 1) and ctx.author in mods_list:
                replystr = "%s You can't kick yourself, silly."
                replystr = (replystr % (ctx.author.mention))
            else:
                replystr = "%s Not even you can kick the likes of %s."
                replystr = (replystr % (ctx.author.mention, ment_mods))

        await ctx.send(replystr)


    @commands.command(name='purge', aliases=['clean', 'cleanup'])
    @commands.check(checks.is_mod)
    async def _purge(self, ctx, *args):
        """Delete a certain number of posts all at once."""
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
            # If message is pinned -> False
            # Author in mentions      True
            # No mentions             True
            # -> Otherwise            False
            if message.pinned:
                return False
            elif message.author in ctx.message.mentions:
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
