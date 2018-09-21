import discord
from discord.ext import commands
from botfunctions import checks, native

# This cog is for commands restricted to mods on a server.
# It features commands such as !ban, !mute, etc.

class ModCmdsCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mute', aliases=['exile', 'banish', 'microexile', 'microbanish'])
    @commands.check(checks.is_mod)
    async def _banish(self, ctx):
        # (Micro)banish and (Micro)exile are functionally the same as mute, except with a custom message
        # and default time limit. The idea for the micro prefix is that it will work more as a statement
        # and only banish the user for a minute or so.
        # Because the mechanics of these functions are so similar - i.e. add a tag and edit the database,
        # I've chosen to clump them into the same function.
        pass

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
    async def _kick(self, ctx):
        # This function kicks the user out of the server in which it is issued.
        todo_list = ctx.message.mentions
        success_list = list()
        fail_list = list()
        mods_list = list()
        forbidden_error = False
        http_error = False
        tried_to_kick_mod = False



        print(ctx.message.content)


        # If they tried to kick a mod christmas is cancelled.
        for victim in todo_list:
            if await checks.is_mod(victim):
                tried_to_kick_mod = True
                mods_list.append(victim)
        ment_mods = native.mentions_list(mods_list)

        # Start the kicking.
        if len(todo_list) > 0 and not tried_to_kick_mod:
            for victim in todo_list:
                try:
                    await ctx.guild.kick(victim)
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
        elif len(todo_list) == 0:
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
