import discord                          # Basic discord functionality
import re                               # Required for certain commands
import asyncio                          # Required for banger !purge message
from internals import checks            # Required to check for mod privilegies
from internals.cogbase import CogBase   # Required inherit colors and stuff

# This cog is for commands restricted to mods on a server.
# It features commands such as !ban, !kick, etc.

def setup(bot):
    bot.add_cog(ModCmdsCog(bot))

class ModCmdsCog(CogBase, name='Moderation'):
    """Good mod! Read the manual! Or if you're not mod - sod off!"""
    def __init__(self, bot):
        self.bot = bot
        self.initialize_colors()

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


    @discord.ext.commands.command(name='say', aliases=['speak', 'chat'])
    @discord.ext.commands.check(checks.is_mod)
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


    @discord.ext.commands.command(name='rules', aliases=['rule'])
    async def _rules(self, ctx, *args):
        """Remind users of what the rules are."""
        rules = {
            1: "Rule 1: Be nice and decent to everyone. Hate speech will not be tolerated.",
            2: "Rule 2: Keep discussions civil and mature.",
            3: "Rule 3: Stay on topic and avoid spamming.",
            4: "Rule 4: Please use common sense when posting here and follow usual Discord etiquette."
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

    @discord.ext.commands.command(name='ban', aliases=['purgeban', 'banpurge'])
    @discord.ext.commands.check(checks.is_mod)
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
        ment_success = self.mentions_list(success_list)
        ment_fail = self.mentions_list(fail_list)

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
            replystr = "Sure, I'll go right ahead and ban... wait who should I ban? You didn't mention anyone? Freeze in hell %s!"
            replystr = (replystr % (ctx.author.mention,))

        elif len(ctx.message.mentions) == len(mods_list):
            # No mentions that weren't mods
            replystr = "%s Every single person on that list of yours is a mod. This is mutiny!"
            replystr = (replystr % (ctx.author.mention,))

        elif (len(success_list) == 1) and (len(fail_list) == 0):
            # Singular success
            replystr = "%s The smuddy little smud %s won't bother us no more, if you know what I mean... :hammer:"
            replystr = (replystr % (ctx.author.mention, ment_success))

        elif (len(success_list) > 1) and (len(fail_list) == 0):
            # Plural success
            ban_hammer = (':hammer:' * len(success_list))
            replystr = "%s Those smuddy little smuds %s won't bother us no more. Because they're all BANNED! %s"
            replystr = (replystr % (ctx.author.mention, ment_success, ban_hammer))

        elif (len(success_list) > 0) and (len(fail_list) > 0):
            # Mixed results
            error_str = error_str.lower().replace('.', '').replace('http', 'HTTP')
            replystr = "%s My powers are disapating, due to %s I wasn't able to ban all of the users requested."
            replystr += "\nBanned: %s\nNot banned: %s"
            replystr = (replystr % (ctx.author.mention, error_str, ment_success, ment_fail))

        elif (len(success_list) == 0) and (len(fail_list) == 1):
            # Singular fail
            error_str = error_str.lower().replace('.', '').replace('http', 'HTTP')
            replystr = "%s The smuddy little smud %s... will actually keep bothering us. I wasn't able to ban them due to %s."
            replystr = (replystr % (ctx.author.mention, ment_fail, error_str))

        elif (len(success_list) == 0) and (len(fail_list) > 1):
            # Plural fail
            ment_fail = ment_fail.replace(' and ', ' or ')
            replystr = "%s I'm deeply ashamed to say that my systems are malfunctioning and I wasn't able to ban %s.\n"
            replystr += "This seems to be due to: %s"
            replystr = (replystr % (ctx.author.mention, ment_fail, error_str))

        if not banlist:
            await ctx.send(replystr)


    @discord.ext.commands.command(name='unban')
    @discord.ext.commands.check(checks.is_mod)
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

        if forbidden_error or http_error:   any_error = True
        else:                               any_error = False

        if forbidden_error and http_error:
            error_str = 'a mix of insufficient privilegies and HTTP issues'
        elif forbidden_error:
            error_str = 'insufficient privilegies'
        elif http_error:
            error_str = 'HTTP issues'
        else:
            error_str = 'unknown error'

        # Now all we need is a reply string.
        ment_success = self.mentions_list(success_list)
        ment_fail = self.mentions_list(fail_list)


        if showbans:
            # This is just a shortcut to invoke the listban command.
            await ctx.invoke(self.bot.get_command('listban'))

        elif not found_anyone and not any_error:
            # No banned users were found in the message.
            replystr = f"{ctx.author.mention} I wasn't able to spot any banned usernames or IDs in that message of yours."

        elif any_error and len(fail_list) == 0:
            # Encountered an error during listing,
            # no unban attempts have been made.
            replystr = f"{ctx.author.mention} Due to {error_str} I wasn't able to retrieve the list of banned users. "
            replystr += "Without that list I can't even try to unban them."

        elif len(success_list) == 1 and len(fail_list) == 0:
            # Singular success, no fails.
            replystr = f"{ctx.author.mention} Smuddy McSmudface, I mean {ment_success}, has been unbanned... for some reason. :shrug:"

        elif len(success_list) > 1 and len(fail_list) == 0:
            # Plural success, no fails.
            replystr = f"{ctx.author.mention} The users known as {ment_success} have been unbanned... but why?"

        elif len(success_list) > 0 and len(fail_list) > 0:
            # Mixed results.
            replystr =  f"{ctx.author.mention} The unbanning was a success! Partially anyway...\n"
            replystr += f"Unbanned user(s): {ment_success}\n"
            replystr += f"Still banned user(s): {ment_fail}\n"
            replystr += f"Failure was caused by {error_str}."

        elif len(success_list) == 0 and len(fail_list) == 1:
            # No success, singular fail.
            replystr = f"{ctx.author.mention} I wasn't able to unban {ment_fail} due to {error_str}."

        elif len(success_list) == 0 and len(fail_list) > 1:
            # No success, plural fails.
            ment_fail = ment_fail.replace(' and ', ' or ')
            replystr = f"{ctx.author.mention} I wasn't able to unban {ment_fail} due to {error_str}."

        else:
            replystr =  f"{ctx.author.mention} Someone call <@!154516898434908160>! I don't know what's going on!!!\n"
            replystr += f"len(success_list) == {len(success_list)}, len(fail_list) == {len(fail_list)}\n"
            replystr += f"http_error == {http_error}, forbidden_error == {forbidden_error}"

        if not showbans:
            await ctx.send(replystr)



    @discord.ext.commands.command(name='listban', aliases=['banlist','listbans','banslist'])
    @discord.ext.commands.check(checks.is_mod)
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
                replystr = f"{ctx.author.mention} There are no banned users... yet. If you'd like to change that just say the word!"

            else:
                replystr = "The following users are currently banned:\n"
                for ban in banlist:
                    add_str = f"**{ban.user.name}#{ban.user.discriminator}** (id: {ban.user.id})"
                    if ban.reason != None:
                        add_str += f"**\n({ban.user.name} was banned for: {ban.reason})"

                    if ban != banlist[-1]:
                        add_str += "\n"

                    replystr += add_str
        else:
            replystr = f"{ctx.author.mention} Due to {error_str} I wasn't able to retrieve the list of banned smuds."

        await ctx.send(replystr)


    @discord.ext.commands.command(name='kick')
    @discord.ext.commands.check(checks.is_mod)
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
        ment_mods = self.mentions_list(mods_list)

        if len(mods_list) == 0: tried_to_kick_mod = False
        else:                   tried_to_kick_mod = True


        # Start the kicking.
        if len(ctx.message.mentions) > 0 and not tried_to_kick_mod:
            for victim in ctx.message.mentions:
                try:
                    if reason == None:
                        await ctx.guild.kick(victim)
                        print(f"{self.WHITE_B}{victim.name}#{victim.discriminator}{self.CYAN} was " +
                            f"{self.RED_B}kicked from {ctx.guild.name} {self.CYAN}by {self.GREEN_B}" +
                            f"{ctx.author.name}#{ctx.author.discriminator}")
                    else:
                        await ctx.guild.kick(victim, reason=reason)
                        print(f"{self.WHITE_B}{victim.name}#{victim.discriminator}{self.CYAN} was " +
                            f"{self.RED_B}kicked from {ctx.guild.name} {self.CYAN}by {self.GREEN_B}" +
                            f"{ctx.author.name}#{ctx.author.discriminator}{self.CYAN}.\n{self.WHITE_B}Reason given: " +
                            f"{self.WHITE}{reason}{self.RESET}")
                    success_list.append(victim)

                except discord.Forbidden:
                    fail_list.append(victim)
                    forbidden_error = True
                    print(f"{self.RED_B}ERROR {self.CYAN}I was not allowed to {self.RED_B}!kick {self.WHITE_B}{victim.name}#{victim.discriminator}" +
                        f"{self.CYAN} in {self.RED_B}{ctx.guild.name}{self.CYAN}.{self.RESET}")

                except discord.HTTPException:
                    fail_list.append(victim)
                    http_error = True
                    print(f"{self.RED_B}ERROR {self.CYAN}I couldn't {self.RED_B}!kick {self.WHITE_B}{victim.name}#{victim.discriminator}" +
                        f"{self.CYAN} in {self.RED_B}{ctx.guild.name} {self.CYAN}due to an HTTP Exception.{self.RESET}")

        # This will convert the lists into mentions suitable for text display:
        # user1, user2 and user 3
        ment_success = self.mentions_list(success_list)
        ment_fail = self.mentions_list(fail_list)

        ### Preparation of replystrings.
        ### Errors are added further down.

        # Had at least one success and no fails.
        if (len(success_list) > 0) and (len(fail_list) == 0):

            # Singular
            if len(success_list) == 1:
                replystr = f"{ctx.author.mention} The smud who goes by the name of {ment_success} "
                replystr += "has been kicked from the server, never to be seen again!"

            # Plural
            else:
                replystr = f"{ctx.author.mention} The smuds who go by the names of {ment_success} "
                replystr += "have been kicked from the server, never to be seen again!"

        # Had no successes and at least one fail.
        elif (len(success_list) == 0) and (len(fail_list) > 0):

            # Singular
            if len(fail_list) == 1:
                replystr = f"{ctx.author.mention} So... it seems I wasn't able to kick {ment_fail} due to: "

            # Plural
            else:
                replystr = f"{ctx.author.mention} So... it seems I wasn't able to kick any of {ment_fail}.\nThis was due to: "

        # Had at least one success and at least one fail.
        elif (len(success_list) > 0) and (len(fail_list) > 0):
            # Singular and plural don't matter here.
            replystr =  f"{ctx.author.mention} The request was executed with mixed results."
            replystr += f"\nKicked: {ment_success}\nNot kicked: {ment_fail}\nThis was due to: "

        # Had no mentions whatsoever.
        elif len(ctx.message.mentions) == 0:
            # Singular and plural don't matter here.
            replystr = f"{ctx.author.mention} You forgot to mention anyone you doofus. Who exactly am I meant to kick??"

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
                replystr = f"{ctx.author.mention} You can't kick yourself, silly."
            else:
                replystr = f"{ctx.author.mention} Not even you can kick the likes of {ment_mods}."

        await ctx.send(replystr)


    @discord.ext.commands.command(name='purge', aliases=['superpurge'])
    @discord.ext.commands.check(checks.is_mod)
    async def _purge(self, ctx, *args):
        """Delete a certain number of posts all at once."""
        # This function will remove the last X number of posts in the channel.
        # Features:
        # - If message contains mentions, it will only delete messages by
        #   the people mentioned.
        # - Limit is 100 messages.
        # - Also deletes message which called the function.

        # Delete the message containing the purge command.
        try:    await ctx.message.delete()
        except: pass

        # We'll use the first number we can find in the arguments.
        # We'll also parse negative numbers so the error message will be better.
        delete_no = 0
        for arg in args:
            if arg.isdigit() or (arg[0] == '-' and arg[1:].isdigit()):
                delete_no = int(arg)
                break

        if delete_no <= 0:
            await ctx.send(f"{ctx.author.mention} You want me to delete {delete_no} messages? Good joke.")
            delete_no = 0

        elif delete_no > 100 and ctx.invoked_with != 'superpurge':
            # For big deletes we post a warning message for a few seconds before deleting.
            message = await ctx.send('`Purge overload detected, engaging safety protocols.`')
            await asyncio.sleep(1)

            await message.edit(content=message.content + '\n`Purge size successfully contained to 100 messages.`')
            await asyncio.sleep(1)

            await message.edit(content=message.content + '\n`Charging phasers...`')
            await asyncio.sleep(1)

            oldmessage = message.content + '\n'

            countdown = 3
            while countdown > 0:
                if countdown == 0:
                    break

                await message.edit(content=
                        oldmessage + f'`Phaser at full charge in... {countdown}`'
                )
                countdown -= 1
                await asyncio.sleep(1)

            delete_no = 101

        def check_func(message):
            # False means don't delete, True means delete.
            # - Don't delete pinned messages.
            # - If there are no mentions in the original message, delete.
            # - If the author is in the list of mentions, delete it.
            # - Also delete if there are no mentions.
            author = message.author
            mentions = ctx.message.mentions
            no_mentions = (len(mentions) == 0)

            if message.pinned:          return False
            elif no_mentions:           return True
            elif author in mentions:    return True
            else:                       return False

        try:
            await ctx.channel.purge(limit=delete_no, check=check_func)

        except discord.Forbidden:
            print(f"{self.RED_B}!purge failed{self.CYAN} in " +
                f"{self.CYAN_B}#{ctx.channel.name}{self.YELLOW_B} @ {self.CYAN_B}{ctx.guild.name}" +
                f"{self.RED_B} (Forbidden){self.RESET}")

            await ctx.send(
                f"{ctx.author.mention} An error occured, it seems I'm lacking the" +
                "privilegies to carry out your Great Purge.")

        except discord.HTTPException:
            print(f"{self.RED_B}!purge failed{self.CYAN} in " +
                f"{self.CYAN_B}#{ctx.channel.name}{self.YELLOW_B} @ {self.CYAN_B}{ctx.guild.name}" +
                f"{self.RED_B} (HTTP Exception){self.RESET}")

            await ctx.send(
                f"{ctx.author.mention} An error occured, it seems my HTTP sockets are " +
                "glitching out and thus I couldn't carry out your Great Purge.")

        except Exception as e:
            print(f"{self.RED_B}!purge failed{self.CYAN} in " +
                f"{self.CYAN_B}#{ctx.channel.name}{self.YELLOW_B} @ {self.CYAN_B}{ctx.guild.name}" +
                f"{self.RED_B}\n({e}){self.RESET}")

            await ctx.send(
                f"{ctx.author.mention} Something went wrong with your Great Purge and I don't really know what.")

    @discord.ext.commands.command(name='idban')
    @discord.ext.commands.check(checks.is_mod)
    async def _idban(self, ctx, *args):
        """Quick and dirty function for banishing via ID. Might flesh it out later or merge with the real ban function."""
        if len(args) > 0 and args[0].isdigit():
            banlist = await ctx.guild.bans()
            new_id = int(args[0])
            new_user = discord.Object(id=new_id)
            try:
                await ctx.guild.ban(new_user)
                await ctx.send('That little smud, whoever it is, has been banned!')
            except Exception as e:
                print(e)
        else:
            await ctx.send(f"{ctx.author.mention} PAPERS PLEASE! :rage:")
