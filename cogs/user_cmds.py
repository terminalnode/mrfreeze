import discord, re, datetime, random
from internals import var
from discord.ext import commands
from internals import native, checks
from databases import regionbl

def setup(bot):
    bot.add_cog(UserCmdsCog(bot))

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

    @commands.command(name='praise')
    async def _praise(self, ctx, *args):
        """Praise me!!"""
        author = ctx.author.mention
        await ctx.send(f"{author} Your praises have been heard, and in return I bestow upon you... nothing!")

    @commands.command(name='icon', aliases=['logo'])
    async def _logo(self, ctx, *args):
        """Post the logo of the current server."""
        author = ctx.author.mention
        server = ctx.guild.name
        word = ctx.invoked_with

        logo = discord.Embed()
        logo.set_image(url=ctx.guild.icon_url_as(format='png'))
        await ctx.send(f"{author} Here's the server {word} for {server}!", embed=logo)

    @commands.command(name='mrfreeze', aliases=['freeze'])
    async def _mrfreeze(self, ctx, *args):
        """Get a quote from my timeless classic "Batman & Robin"!"""
        author = ctx.author.mention
        server = ctx.guild.name

        with open('config/mrfreezequotes', 'r') as f:
            quote = random.choice(f.read().strip().split('\n'))

        quote = quote.replace('Batman', author)
        quote = quote.replace('Gotham', f"**{server}**")
        await ctx.send(quote)


    @commands.command(name='cointoss', aliases=['coin', 'coinflip'])
    async def _cointoss(self, ctx, *args):
        """Toss a coin, results are 50/50."""
        if random.randint(0,1): await ctx.send(f"{ctx.author.mention} Heads")
        else:                   await ctx.send(f"{ctx.author.mention} Tails")


    @commands.command(name='vote', aliases=['election', 'choice', 'choose'])
    async def _vote(self, ctx, *args):
        """Create a handy little vote using reacts."""
        def find_custom_emoji(line):
            emoji = re.match('<a?:\w+:(\d+)>', line)

            if emoji == None:
                # Non-custom emoji can be up to three characters long.
                return line[0:3]
            else:
                emo_id = emoji.group(1)
                return self.bot.get_emoji(int(emo_id))

        async def add_reacts(reacts):
            react_error = False
            at_least_one = False
            if None in reacts:  nitro_error = True
            else:               nitro_error = False

            for react in reacts:
                if isinstance(react, discord.Emoji):
                    try:
                        await ctx.message.add_reaction(react)
                        at_least_one = True
                    except: react_error = True

                elif isinstance(react, str):
                    string_options = (react, react[0:2], react[0])
                    for option in string_options:
                        try:
                            await ctx.message.add_reaction(option)
                            at_least_one = True
                            break
                        except: pass

            if react_error:
                print(f"{var.red}!vote{var.cyan} Not allowed to add react in {ctx.guild.name}{var.reset}")
                await ctx.send(f"{ctx.author.mention} The moderators dun goofed I think. I encountered some sort of anomaly when trying to vote.")
            elif nitro_error:
                await ctx.send(f"{ctx.author.mention} There seem to be some emoji there I don't have access to.\nI need to be in the server the emoji is from.")
            elif not at_least_one:
                await ctx.send(f"{ctx.author.mention} There's literally nothing I can vote for you little smudmeister!")

        rows = ctx.message.content.split('\n')
        rows[0] = rows[0].replace('!vote ', '')
        reacts = [ find_custom_emoji(row) for row in rows ]
        await add_reacts(reacts)

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
