import discord, re, datetime, random
from discord.ext import commands
from internals import native, checks
from databases import regionbl

class UserCmdsCog(commands.Cog, name='Everyone'):
    """These are the fun commands, everything else is boring and lame. Frankly there's no reason you should pay attention to anything that's not on this page."""
    def __init__(self, bot):
        self.bot = bot
        self.region_ids = dict()

    @commands.Cog.listener()
    async def on_ready(self):
        # Creating dict of all the region role ids
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


    @commands.command(name='mrfreeze', aliases=['freeze'])
    async def _mrfreeze(self, ctx, *args):
        """Get a quote from my timeless classic "Batman & Robin"!"""
        with open('config/mrfreezequotes', 'r') as f:
            quote = random.choice(f.read().strip().split('\n'))

        quote = quote.replace('Batman', ctx.author.mention)
        quote = quote.replace('Gotham', ('**' + ctx.guild.name + '**'))
        await ctx.send(quote)


    @commands.command(name='cointoss', aliases=['coin', 'coinflip'])
    async def _cointoss(self, ctx, *args):
        """Toss a coin, results are 50/50."""
        if random.randint(0,1): await ctx.send(f"{ctx.author.mention} Heads")
        else:                   await ctx.send(f"{ctx.author.mention} Tails")


    @commands.command(name='vote', aliases=['election', 'choice', 'choose'])
    async def _vote(self, ctx, *args):
        """Create a handy little vote using reacts."""
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
        """Assign yourself a colourful regional role."""
        await ctx.send("!region is currently out of service.")

    @commands.command(name='activity', aliases=['listen', 'listening', 'playing', 'play', 'game', 'gaming', 'gameing', 'stream', 'streaming', 'watch', 'watching'])
    # @commands.cooldown(1, (60*10), BucketType.default)
    async def _activity(self, ctx, *args):
        """Dictate what text should be displayed under my nick."""
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
            for activity in activity_types:
                for alias in activity_types[activity]:
                    if (len(args) >= 1) and (args[0] == alias):
                        chosen_activity = activity
                        args = args[1:]

                    elif (len(args) >= 2) and (args[0] == 'is') and (args[1] == alias):
                        chosen_activity = activity
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
                    activity_obj = discord.Activity(name=joint_args,
                                                    type=chosen_activity)
                    await self.bot.change_presence(activity=activity_obj)
                    success = True
                except:
                    pass

        if chosen_activity == discord.ActivityType.playing:
            reply_activity = 'playing'
        elif chosen_activity == discord.ActivityType.streaming:
            # streaming doesn't work as I want it, always says playing not streaming.
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
            replystr = '%s That activity is stupidly long (%s characters). Limit is %s characters.'
            replystr = (replystr % (ctx.author.mention, str(len(joint_args)), str(max_activity_length)))
            await ctx.send(replystr)

        else:
            replystr = '<@!154516898434908160> Something went wrong when trying to change my activity and I have no idea what. Come see!'
            await ctx.send(replystr)


def setup(bot):
    bot.add_cog(UserCmdsCog(bot))
