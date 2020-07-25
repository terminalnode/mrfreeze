"""Module for the Moderation cog, used to for commands pertaining to moderation."""

import asyncio
import logging
import re
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import discord
from discord import Embed
from discord import Message
from discord import Role
from discord import TextChannel
from discord.ext.commands import Cog
from discord.ext.commands import Context
from discord.ext.commands import check
from discord.ext.commands import command

from mrfreeze.bot import MrFreeze
from mrfreeze.lib import checks
from mrfreeze.lib import default
from mrfreeze.lib.colors import CYAN
from mrfreeze.lib.colors import CYAN_B
from mrfreeze.lib.colors import GREEN_B
from mrfreeze.lib.colors import RED_B
from mrfreeze.lib.colors import RESET
from mrfreeze.lib.colors import WHITE
from mrfreeze.lib.colors import WHITE_B
from mrfreeze.lib.colors import YELLOW_B


def setup(bot: MrFreeze) -> None:
    """Add the cog to the bot."""
    bot.add_cog(Moderation(bot))


class Moderation(Cog):
    """
    Cog for commands pertaining to moderation.

    It features command such as !ban, !kick and so on.
    """

    def __init__(self, bot: MrFreeze) -> None:
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract_reason(self, reason: str) -> Optional[str]:
        """Return anything mentioned after the list of mentions."""
        output = reason
        in_mention = False
        for letter in range(len(reason)):

            # If the current and two following characters form <@ and a digit,
            # we assume that we're in a mention.
            if (reason[letter:letter + 2] == '<@') and (reason[letter + 2].isdigit()):
                in_mention = True

            # If we're in a mention and detect the closing >, we'll add all
            # trailing characters to the output. These two steps are repeated
            # until we have an output void of any mentions.
            if in_mention and (reason[letter] == '>'):
                in_mention = False
                output = reason[(letter + 1):]

        # If there's nothing left after these steps we'll return None.
        # Otherwise we'll return the output.
        if len(output.strip()) == 0:
            return None
        else:
            return output.strip()

    @command(name="freezemute", aliases=["shutup", "mutefreeze"])
    @check(checks.is_owner_or_mod)
    async def freezemute(self, ctx: Context, *args: str) -> None:
        """
        Make freeze ignore all commands except this one in a server.

        The mute is togglable, to reenable freeze in a server just
        run the command again.
        """
        if self.bot.user not in ctx.message.mentions:
            return

        # Toggle mute
        self.bot.settings.toggle_freeze_mute(ctx.guild)

        # Check if freeze is now muted and respond accordingly
        is_muted = self.bot.settings.is_freeze_muted(ctx.guild)
        mention = ctx.author.mention
        if is_muted:
            await ctx.send(
                f"{mention} Ok... I'll ignore all commands in this server until further notice.")
        else:
            await ctx.send(
                f"{mention} Yay I'm back!!")

    @command(name="trashchannel", aliases=["settrashchannel"])
    @check(checks.is_owner_or_mod)
    async def set_trash_channel(self, ctx: Context, channel: TextChannel, *args: str) -> None:
        """Set the trash channel for the given server."""
        mention = ctx.author.mention
        old_channel = "nothing"
        new_channel = "something"

        old_cid = self.bot.settings.get_trash_channel(ctx.guild)
        result = self.bot.settings.set_trash_channel(channel)
        new_cid = self.bot.settings.get_trash_channel(ctx.guild)

        try:
            new_channel = (await self.bot.fetch_channel(new_cid)).mention
            old_channel = (await self.bot.fetch_channel(old_cid)).mention
        except Exception:
            pass

        if not result:
            reply  = f"{mention} Something went wrong, the trash channel has not been changed."
        elif old_cid == new_cid:
            reply  = f"{mention} The trash channel was already set to "
            reply += f"{new_channel}, but good on you for making sure!"
        else:
            reply  = f"{mention} The dedicated trash channel has been changed from "
            reply += f"{old_channel} to {new_channel}."

        await ctx.send(reply)

    @command(name="mutechannel", aliases=["setmutechannel"])
    @check(checks.is_owner_or_mod)
    async def set_mute_channel(self, ctx: Context, channel: TextChannel, *args: str) -> None:
        """Set the mute channel for the given server."""
        mention = ctx.author.mention
        old_channel = "nothing"
        new_channel = "something"

        old_cid = self.bot.settings.get_mute_channel(ctx.guild)
        result = self.bot.settings.set_mute_channel(channel)
        new_cid = self.bot.settings.get_mute_channel(ctx.guild)

        try:
            new_channel = (await self.bot.fetch_channel(new_cid)).mention
            old_channel = (await self.bot.fetch_channel(old_cid)).mention
        except Exception:
            pass

        if not result:
            reply  = f"{mention} Something went wrong, the mute channel has not been changed."
        elif old_cid == new_cid:
            reply  = f"{mention} The mute channel was already set to "
            reply += f"{new_channel}, but good on you for making sure!"
        else:
            reply  = f"{mention} The dedicated mute channel has been changed from "
            reply += f"{old_channel} to {new_channel}."

        await ctx.send(reply)

    @command(name="muterole", aliases=["setmuterole"])
    @check(checks.is_owner_or_mod)
    async def set_mute_role(self, ctx: Context, channel: Role, *args: str) -> None:
        """Set the mute role for the given server."""
        pass

    @command(name='say', aliases=['speak', 'chat'])
    @check(checks.is_owner_or_mod)
    async def _say(self, ctx: Context, channel: TextChannel, *args: str) -> None:
        """Let me be your voice."""
        replystr = ' '.join(args)

        # Now let's find all the custom emoji to make sure they all work.
        # If any of them don't, halt operations.
        emoji = re.findall(r"<a?:\w+:(\d+)(?=>)", replystr)
        impossible = False
        for i in emoji:
            if self.bot.get_emoji(int(i)) is None:
                impossible = True
                break

        # If a string of numbers is found, see if it's a user ID.
        # 1. Find strings of numbers not belonging to a mention.
        # 2. See if that number is a user ID for anyone we know.
        users = re.findall(r"(?:\s|^)(\d+)", replystr)
        users = [ctx.guild.get_member(int(user))
                 for user in users
                 if ctx.guild.get_member(int(user)) is not None]
        for user in users:
            replystr = replystr.replace(str(user.id), user.mention)
            replystr = replystr.replace(f'<@!<@!{user.id}>>', user.mention)

        if impossible:
            reply =  f"{ctx.author.mention} Abort! Abort! There are emoji "
            reply += "in your message that I can't use.."
            await ctx.channel.send(reply)
        else:
            await channel.send(replystr)

    @command(name="rules", aliases=["rule"])
    async def _rules(self, ctx: Context, *args: str) -> None:
        """Remind users of what the rules are."""
        rule_1  = "Rule 1: Be nice and decent to everyone. Hate speech will not be tolerated."
        rule_2  = "Rule 2: Keep discussions civil and mature."
        rule_3  = "Rule 3: Stay on topic and avoid spamming."
        rule_4  = "Rule 4: Please use common sense when posting here "
        rule_4 += "and follow usual Discord etiquette."
        rule_5  = "Rule 5: Political discussion is not allowed."
        rules = { 1: rule_1, 2: rule_2, 3: rule_3, 4: rule_4, 5: rule_5 }

        rule_triggers: Dict[int, Tuple[str, ...]] = {
            1: ("1", "joke", "jokes", "joking", "sex", "sexual", "weight",
                "race", "skin", "color", "colour", "gender", "nice", "decent",
                "hate"),
            2: ("2", "civil", "civility", "mature", "maturity", "disagreement",
                "dismissive", "dismissal", "opinion", "opinions", "shoe",
                "shoes", "shoesize", "age", "act", "behave"),
            3: ("3", "topic", "ontopic", "offtopic", "spam", "nonsense"),
            4: ("4", "sense", "etiquette", "ettiquette"),
            5: ("5", "politic", "politics", "political")
        }

        request = " ".join(args).lower()
        called_rules = str()

        if "all" in request:
            for rule in rules:
                called_rules += f"{rules[rule]}\n"
        else:
            for rule in rule_triggers:
                for keyword in rule_triggers[rule]:
                    if keyword in request and str(rule) not in called_rules:
                        called_rules += f"{rules[rule]}\n"

        if len(called_rules) == 0:
            reply  = f"Sorry {ctx.author.mention}, your terms don't "
            reply += "seem to match any rules. :thinking:"
            await ctx.send(reply)
        else:
            await ctx.send(called_rules.strip())

    @command(name='ban', aliases=['purgeban', 'banpurge'])
    @check(checks.is_mod)
    async def _ban(self, ctx: Context, *args: str) -> None:
        """Remove a user from our sight - permanently."""
        # This function simply bans a user from the server in which it's issued
        reason = self.extract_reason(" ".join(args))
        forbidden_error = False
        http_error = False
        success_list = list()
        fail_list = list()

        if "list" in args:
            # This is just a shortcut to invoke the listban command.
            banlist = True
        else:
            banlist = False

        if ctx.invoked_with == "ban":
            do_purge = False
        else:
            do_purge = True

        mod_role = discord.utils.get(ctx.guild.roles, name="Administration")
        mods_list = [user
                     for user in ctx.message.mentions
                     if mod_role in user.roles]

        for victim in [user
                       for user in ctx.message.mentions
                       if user not in mods_list]:
            try:
                if not do_purge:
                    await ctx.guild.ban(victim,
                                        reason=reason,
                                        delete_message_days=0)
                else:
                    await ctx.guild.ban(victim,
                                        reason=reason,
                                        delete_message_days=7)

                success_list.append(victim)

            except discord.Forbidden:
                forbidden_error = True
                fail_list.append(victim)

            except discord.HTTPException:
                http_error = True
                fail_list.append(victim)

        # And now we compile a response.
        ment_success = default.mentions_list(success_list)
        ment_fail = default.mentions_list(fail_list)

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
            replystr = "Sure, I'll go right ahead and ban... wait who should I ban? "
            replystr += f"You didn't mention anyone? Freeze in hell {ctx.author.mention}!"

        elif len(ctx.message.mentions) == len(mods_list):
            # No mentions that weren't mods
            replystr  = f"{ctx.author.mention} Every single person on that list of yours "
            replystr += "is a mod. This is mutiny!"

        elif (len(success_list) == 1) and (len(fail_list) == 0):
            # Singular success
            replystr  = f"{ctx.author.mention} The smuddy little smud {ment_success} won't "
            replystr += "bother us no more, if you know what I mean... :hammer:"

        elif (len(success_list) > 1) and (len(fail_list) == 0):
            # Plural success
            ban_hammer = (":hammer:" * len(success_list))
            replystr  = f"{ctx.author.mention} Those smuddy little smuds {ment_success} "
            replystr += f"won't bother us no more. Because they're all BANNED! {ban_hammer}"

        elif (len(success_list) > 0) and (len(fail_list) > 0):
            # Mixed results
            error_str = error_str.lower().replace('.', '').replace('http', 'HTTP')
            replystr  = f"{ctx.author.mention} My powers are disapating, due to {error_str} "
            replystr += "I wasn't able to ban all of the users requested."
            replystr += f"\nBanned: {ment_success}\nNot banned: {ment_fail}"

        elif (len(success_list) == 0) and (len(fail_list) == 1):
            # Singular fail
            error_str = error_str.lower().replace('.', '').replace('http', 'HTTP')
            replystr  = f"{ctx.author.mention} The smuddy little smud {ment_fail}... will "
            replystr += "actually keep bothering us. I wasn't able to ban them due "
            replystr += f"to {error_str}."

        elif (len(success_list) == 0) and (len(fail_list) > 1):
            # Plural fail
            ment_fail = ment_fail.replace(' and ', ' or ')
            replystr  = f"{ctx.author.mention} I'm deeply ashamed to say that my systems "
            replystr += f"are malfunctioning and I wasn't able to ban {ment_fail}.\n"
            replystr += f"This seems to be due to: {error_str}"

        if not banlist:
            await ctx.send(replystr)

    @command(name="unban")
    @check(checks.is_mod)
    async def _unban(self, ctx: Context, *args: str) -> None:
        """Unpermanent removal from sight of a previously banned user."""
        forbidden_error = False
        http_error = False
        banlist = list()

        # This is a shortcut to invoke the banlist command with !unban list.
        if args == ("list",):
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
        usr_names = re.findall(r"(?<=\s)\S+#\d{4}(?=\s)", (" " + ctx.message.content + " "))
        usr_ids = re.findall(r"(?<=\s)\d+(?=\s)", (" " + ctx.message.content + " "))

        success_list = list()
        fail_list = list()
        found_anyone = False
        for ban_entry in banlist:
            user = ban_entry.user
            user_str = f"{user.name}#{user.discriminator}"

            # Below is an easy and expandable way to add criterias for unban.
            # Every if-statement corresponds to one criteria.
            #
            # For example we could easily add this as an extra criteria
            # if we wanted to. This would match any username, not requiring
            # the #identifier

            if user_str in usr_names:
                entry_hit = True
            elif (str(user.id) in usr_ids):
                entry_hit = True
            else:
                entry_hit = False

            # If any of the above resulted in a hit we'll try to remove the ban
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

        any_error = False
        if forbidden_error or http_error:
            any_error = True

        if forbidden_error and http_error:
            error_str = 'a mix of insufficient privilegies and HTTP issues'
        elif forbidden_error:
            error_str = 'insufficient privilegies'
        elif http_error:
            error_str = 'HTTP issues'
        else:
            error_str = 'unknown error'

        # Now all we need is a reply string.
        ment_success = default.mentions_list(success_list)
        ment_fail = default.mentions_list(fail_list)

        if showbans:
            # This is just a shortcut to invoke the listban command.
            await ctx.invoke(self.bot.get_command('listban'))

        elif not found_anyone and not any_error:
            # No banned users were found in the message.
            replystr  = f"{ctx.author.mention} I wasn't able to spot any banned usernames "
            replystr += "or IDs in that message of yours."

        elif any_error and len(fail_list) == 0:
            # Encountered an error during listing,
            # no unban attempts have been made.
            replystr  = f"{ctx.author.mention} Due to {error_str} I wasn't able to "
            replystr += "retrieve the list of banned users. Without that list I can't "
            replystr += "even try to unban them."

        elif len(success_list) == 1 and len(fail_list) == 0:
            # Singular success, no fails.
            replystr  = f"{ctx.author.mention} Smuddy McSmudface, I mean {ment_success}, "
            replystr += "has been unbanned... for some reason. :shrug:"

        elif len(success_list) > 1 and len(fail_list) == 0:
            # Plural success, no fails.
            replystr  = f"{ctx.author.mention} The users known as {ment_success} "
            replystr += "have been unbanned... but why?"

        elif len(success_list) > 0 and len(fail_list) > 0:
            # Mixed results.
            replystr  = f"{ctx.author.mention} The unbanning was a success! Partially anyway...\n"
            replystr += f"Unbanned user(s): {ment_success}\n"
            replystr += f"Still banned user(s): {ment_fail}\n"
            replystr += f"Failure was caused by {error_str}."

        elif len(success_list) == 0 and len(fail_list) == 1:
            # No success, singular fail.
            replystr  = f"{ctx.author.mention} I wasn't able to unban "
            replystr += f"{ment_fail} due to {error_str}."

        elif len(success_list) == 0 and len(fail_list) > 1:
            # No success, plural fails.
            ment_fail = ment_fail.replace(' and ', ' or ')
            replystr  = f"{ctx.author.mention} I wasn't able to unban "
            replystr += f"{ment_fail} due to {error_str}."

        else:
            replystr  = f"{ctx.author.mention} Quick someone call <@!154516898434908160>! "
            replystr += "I don't know what's going on!!!\n"

        if not showbans:
            await ctx.send(replystr)

    @command(name="listban", aliases=["banlist", "listbans", "banslist"])
    @check(checks.is_mod)
    async def _listban(self, ctx: Context) -> None:
        """Get a list of all banned users (useful for unbanning)."""
        # Because it's tricky to find the exact user name/id when you can't
        # highlight people, this function exists to get easy access to the
        # list of bans in order to unban.

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
            error_str = "insufficient privilegies"
        elif not forbidden_error and http_error:
            error_str = "HTTP issues"
        else:
            # This shouldn't happen, but you can never be too sure.
            error_str = "a mix of insufficient privilegies and HTTP issues"

        if not general_error:
            if len(banlist) == 0:
                replystr  = f"{ctx.author.mention} There are no banned users... yet. "
                replystr += "If you'd like to change that just say the word!"

            else:
                replystr = "The following users are currently banned:\n"
                for ban in banlist:
                    add_str = f"**{ban.user.name}#{ban.user.discriminator}** (id: {ban.user.id})"
                    if ban.reason is not None:
                        add_str += f"\n({ban.user.name} was banned for: {ban.reason})"

                    if ban != banlist[-1]:
                        add_str += "\n"

                    replystr += add_str
        else:
            replystr = f"{ctx.author.mention} Due to {error_str} "
            replystr += "I wasn't able to retrieve the list of banned smuds."

        await ctx.send(replystr)

    @command(name="kick", aliases=["yeet"])
    @check(checks.is_mod)
    async def _kick(self, ctx: Context, *args: str) -> None:
        """Force a user to leave the server temporarily."""
        success_list = list()
        fail_list = list()
        mods_list = list()
        mentions = ctx.message.mentions
        forbidden_error = False
        http_error = False
        reason = self.extract_reason(" ".join(args))
        verb = ctx.invoked_with

        # If they tried to kick a mod christmas is cancelled.
        mods_list = [ user for user in mentions if user.guild_permissions.administrator ]
        ment_mods = default.mentions_list(mods_list)

        tried_to_kick_mod = False
        if len(mods_list) > 0:
            tried_to_kick_mod = True

        # Start the kicking.
        if len(mentions) > 0 and not tried_to_kick_mod:
            for victim in mentions:
                try:
                    if reason is None:
                        await ctx.guild.kick(victim)
                        status  = f"{WHITE_B}{victim.name}#{victim.discriminator}{CYAN} was "
                        status += f"{RED_B}{verb}ed from {ctx.guild.name} {CYAN}by {GREEN_B}"
                        status += f"{ctx.author.name}#{ctx.author.discriminator}"
                    else:
                        await ctx.guild.kick(victim, reason=reason)
                        status  = f"{WHITE_B}{victim.name}#{victim.discriminator}{CYAN} was "
                        status += f"{RED_B}{verb}ed from {ctx.guild.name} {CYAN}by {GREEN_B}"
                        status += f"{ctx.author.name}#{ctx.author.discriminator}{CYAN}."
                        status += f"\n{WHITE_B}Reason given: {WHITE}{reason}{RESET}"
                    success_list.append(victim)
                    self.logger.info(status)

                except discord.Forbidden:
                    fail_list.append(victim)
                    forbidden_error = True

                    status = f"{RED_B}ERROR {CYAN}I was not allowed to {RED_B}!{verb} "
                    status += f"{WHITE_B}{victim.name}#{victim.discriminator}"
                    status += f"{CYAN} in {RED_B}{ctx.guild.name}{CYAN}.{RESET}"
                    self.logger.info(status)

                except discord.HTTPException:
                    fail_list.append(victim)
                    http_error = True

                    status = f"{RED_B}ERROR {CYAN}I couldn't {RED_B}!{verb} {WHITE_B}"
                    status += f"{victim.name}#{victim.discriminator}{CYAN} in {RED_B}"
                    status += f"{ctx.guild.name} {CYAN}due to an HTTP Exception.{RESET}"
                    self.logger.info(status)

        # This will convert the lists into mentions suitable for text display:
        # user1, user2 and user 3
        ment_success = default.mentions_list(success_list)
        ment_fail = default.mentions_list(fail_list)

        # Preparation of replystrings.
        # Errors are added further down.

        # Had at least one success and no fails.
        if (len(success_list) > 0) and (len(fail_list) == 0):

            # Singular
            if len(success_list) == 1:
                replystr = f"{ctx.author.mention} The smud who goes by the name of {ment_success} "
                replystr += f"has been {verb}ed from the server, never to be seen again!"

            # Plural
            else:
                replystr = f"{ctx.author.mention} The smuds who go by the names of {ment_success} "
                replystr += f"have been {verb}ed from the server, never to be seen again!"

        # Had no successes and at least one fail.
        elif (len(success_list) == 0) and (len(fail_list) > 0):

            # Singular
            if len(fail_list) == 1:
                replystr  = f"{ctx.author.mention} So... it seems I wasn't able to {verb} "
                replystr += f"{ment_fail} due to: "

            # Plural
            else:
                replystr  = f"{ctx.author.mention} So... it seems I wasn't able to "
                replystr += f"{verb} any of {ment_fail}.\nThis was due to: "

        # Had at least one success and at least one fail.
        elif (len(success_list) > 0) and (len(fail_list) > 0):
            # Singular and plural don't matter here.
            replystr =  f"{ctx.author.mention} The request was executed with mixed results."
            replystr += f"\n{verb.capitalize()}ed: {ment_success}\n"
            replystr += f"Not {verb.capitalize()}ed: {ment_fail}\nThis was due to: "

        # Had no mentions whatsoever.
        elif len(mentions) == 0:
            # Singular and plural don't matter here.
            replystr  = f"{ctx.author.mention} You forgot to mention anyone "
            replystr += "you doofus. Who exactly am I meant to {verb}??"

        # Now we're adding in the error codes if there are any.
        if forbidden_error and http_error:
            replystr += "Insufficient privilegies and HTTP exception."
        elif not forbidden_error and http_error:
            replystr += "HTTP exception."
        elif forbidden_error and not http_error:
            replystr += "Insufficient privilegies."

        # Finally, a special message to people who tried to kick a mod.
        if tried_to_kick_mod:
            if (len(mods_list) == 1) and ctx.author in mods_list:
                replystr = f"{ctx.author.mention} You can't {verb} yourself, silly."
            elif (len(mods_list)) == 1:
                replystr = f"{ctx.author.mention} Unfortunately you can't {verb} "
                replystr += f"{ment_mods}, because they're a mod."
            else:
                replystr = f"{ctx.author.mention} Unfortunately you can't {verb} "
                replystr += f"{ment_mods}, because they're mods."

        await ctx.send(replystr)

    @command(name="purge", aliases=["superpurge"])
    @check(checks.is_mod)
    async def _purge(self, ctx: Context, *args: str) -> None:
        """
        Delete a certain number of posts all at once.

        This function will remove the last X number of posts in the channel.
        Features:
        - If message contains mentions, it will only delete messages by the people mentioned.
        - Limit is 100 messages.
        - Also deletes message which called the function.
        """
        # Delete the message containing the purge command.
        try:
            await ctx.message.delete()
        except Exception:
            pass

        # We'll use the first number we can find in the arguments.
        # We'll also parse negative numbers so the error message will be better
        delete_no = 0
        for arg in args:
            if arg.isdigit() or (arg[0] == "-" and arg[1:].isdigit()):
                delete_no = int(arg)
                break

        if delete_no <= 0:
            reply = f"{ctx.author.mention} You want me to delete {delete_no} messages? Good joke."
            await ctx.send(reply)
            delete_no = 0

        elif delete_no > 100 and ctx.invoked_with != "superpurge":
            # For big deletes we post a warning message for a few seconds before deleting.
            message = await ctx.send("`Purge overload detected, engaging safety protocols.`")
            await asyncio.sleep(1)

            new_message = message.content + "\n`Purge size successfully contained to 100 messages`"
            await message.edit(content=new_message)
            await asyncio.sleep(1)

            new_message = message.content + "\n`Charging phasers...`"
            await message.edit(content=new_message)
            await asyncio.sleep(1)

            oldmessage = f"{message.content}\n"

            countdown = 3
            while countdown > 0:
                if countdown == 0:
                    break

                new_message = oldmessage + f"`Phaser at full charge in... {countdown}`"
                await message.edit(content=new_message)
                countdown -= 1
                await asyncio.sleep(1)

            delete_no = 101

        def check_func(message: Message) -> bool:
            """
            Determine which messages to keep/delete.

            False means don't delete, True means delete.
            - Don't delete pinned messages.
            - If there are no mentions in the original message, delete.
            - If the author is in the list of mentions, delete it.
            - Also delete if there are no mentions.
            """
            author = message.author
            mentions = ctx.message.mentions
            no_mentions = (len(mentions) == 0)

            if message.pinned:
                return False
            elif no_mentions:
                return True
            elif author in mentions:
                return True
            else:
                return False

        try:
            await ctx.channel.purge(limit=delete_no, check=check_func)

        except discord.Forbidden:
            status  = f"{RED_B}!purge failed{CYAN} in "
            status += f"{CYAN_B}#{ctx.channel.name}{YELLOW_B} @ {CYAN_B}{ctx.guild.name}"
            status += f"{RED_B} (Forbidden){RESET}"
            self.logger.error(status)

            reply  = f"{ctx.author.mention} An error occured, it seems I'm lacking the"
            reply += "privilegies to carry out your Great Purge."
            await ctx.send(reply)

        except discord.HTTPException:
            status  = f"{RED_B}!purge failed{CYAN} in "
            status += f"{CYAN_B}#{ctx.channel.name}{YELLOW_B} @ {CYAN_B}{ctx.guild.name}"
            status += f"{RED_B} (HTTP Exception){RESET}"
            self.logger.error(status)

            reply  = f"{ctx.author.mention} An error occured, it seems my HTTP sockets are "
            reply += "glitching out and thus I couldn't carry out your Great Purge."
            await ctx.send(reply)

        except Exception as e:
            status  = f"{RED_B}!purge failed{CYAN} in {CYAN_B}#{ctx.channel.name}"
            status += f"{YELLOW_B} @ {CYAN_B}{ctx.guild.name}{RED_B}\n({e}){RESET}"
            self.logger.error(status)

            reply  = f"{ctx.author.mention} Something went wrong with your Great Purge "
            reply += "and I don't really know what."
            await ctx.send(reply)

    @command(name="idban", aliases=["banid"])
    @check(checks.is_mod)
    async def _idban(self, ctx: Context, *args: str) -> None:
        """
        Ban users by ID.

        Quick and dirty function for banishing via ID.
        Might flesh it out later or merge with the real ban function.
        """
        if len(args) > 0 and args[0].isdigit():
            new_id = int(args[0])
            new_user = discord.Object(id=new_id)
            try:
                await ctx.guild.ban(new_user)
                await ctx.send("That little smud, whoever it is, has been banned!")
            except Exception as e:
                self.logger.error(e)
        else:
            await ctx.send(f"{ctx.author.mention} PAPERS PLEASE! :rage:")

    @discord.ext.commands.command(name="copy")
    @check(checks.is_mod)
    async def copy(self, ctx: Context, destination: TextChannel, *msg_ids: int) -> None:
        """Copy specified message(s) to specified channel."""
        messages: List[Optional[Message]]
        messages = [ await self.find_message(ctx, id) for id in msg_ids ]

        if None in messages:
            msg = f"{ctx.author.mention} failed to find one or more "
            msg += "of the specified posts. Operation has been cancelled."
            await ctx.send(msg)

            log = f"Message copy by {ctx.author.name} in #{ctx.channel.name} "
            log += f"@ {ctx.guild.name} failed. Could not find all the messages."
            self.logger.info(log)

            return

        for message in messages:
            await self.repost_message(message, destination)

    @discord.ext.commands.command(name="move")
    @check(checks.is_mod)
    async def move(self, ctx: Context, destination: TextChannel, *msg_ids: int) -> None:
        """Copy specified message(s) to specified channel, then delete them."""
        messages: List[Optional[Message]]
        messages = [ await self.find_message(ctx, id) for id in msg_ids ]

        if None in messages:
            msg = f"{ctx.author.mention} failed to find one or more "
            msg += "of the specified posts. Operation has been cancelled."
            await ctx.send(msg)

            log = f"Message move by {ctx.author.name} in #{ctx.channel.name} "
            log += f"@ {ctx.guild.name} failed. Could not find all the messages."
            self.logger.info(log)

            return

        for message in messages:
            repost = await self.repost_message(message, destination)

            # We know message is not None, but mypy doesn't.
            if repost is not None and message is not None:
                await message.delete()

    async def find_message(self, ctx: Context, id: int) -> Optional[Message]:
        """Find the specified message in the channel defined by the context."""
        channel: TextChannel
        message: Optional[Message]

        channel = ctx.channel
        try:
            message = await channel.fetch_message(id)
        except Exception:
            message = None

        return message

    async def repost_message(self, msg: Message, channel: TextChannel) -> Optional[Message]:
        """Repost the message in the designated channel."""
        embed: Embed
        content: str = msg.content
        name: str = msg.author.name
        avatar: str = msg.author.avatar_url

        embed = Embed(color=0x00dee9, description = content)
        embed.set_author(name = name, icon_url = avatar)

        try:
            return await channel.send(embed=embed)
        except Exception:
            return None
