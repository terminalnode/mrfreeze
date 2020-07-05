import discord  # Required for basic discord functionality
import re       # Required for !vote to find custom emoji
import random   # Required for !cointoss and !mrfreeze
from mrfreeze.cogs.cogbase import CogBase
from mrfreeze import colors


def setup(bot):
    """Add the cog to the bot."""
    bot.add_cog(UserCommands(bot))


class UserCommands(CogBase):
    """
    These are the fun commands, everything else is
    boring and lame. Frankly there's no reason you should pay
    attention to anything that's not on this page.
    """
    def __init__(self, bot):
        self.bot = bot

    @CogBase.listener()
    async def on_ready(self):
        pass

    @discord.ext.commands.command(name="praise")
    async def _praise(self, ctx, *args):
        """Praise me."""
        author = ctx.author.mention
        await ctx.send(f"{author} Your praises have been heard, and " +
                       "in return I bestow upon you... nothing!")

    @discord.ext.commands.command(name="icon", aliases=["logo"])
    async def _logo(self, ctx, *args):
        """Post the logo of the current server."""
        author = ctx.author.mention
        server = ctx.guild.name
        word = ctx.invoked_with

        logo = discord.Embed()
        logo.set_image(
            url=ctx.guild.icon_url_as(format="png")
        )
        await ctx.send(
            f"{author} Here's the server {word} for {server}!",
            embed=logo)

    @discord.ext.commands.command(name="mrfreeze", aliases=["freeze"])
    async def _mrfreeze(self, ctx, *args):
        """Get a quote from my timeless classic "Batman & Robin"."""
        author = ctx.author.mention
        server = ctx.guild.name

        with open("config/mrfreezequotes", "r") as f:
            quote = random.choice(f.read().strip().split('\n'))

        quote = quote.replace("Batman", author)
        quote = quote.replace("Gotham", f"**{server}**")
        await ctx.send(quote)

    @discord.ext.commands.command(name="cointoss",
                                  aliases=["coin", "coinflip"])
    async def _cointoss(self, ctx, *args):
        """Toss a coin, results are 50/50."""
        if random.randint(0, 1):
            await ctx.send(f"{ctx.author.mention} Heads")
        else:
            await ctx.send(f"{ctx.author.mention} Tails")

    @discord.ext.commands.command(name="vote",
                                  aliases=["election", "choice", "choose"])
    async def _vote(self, ctx, *args):
        """Create a handy little vote using reacts."""
        def find_custom_emoji(line):
            emoji = re.match(r"<a?:\w+:(\d+)>", line)

            if emoji is None:
                # Non-custom emoji can be up to three characters long.
                return line[0:3]
            else:
                emo_id = emoji.group(1)
                return self.bot.get_emoji(int(emo_id))

        async def add_reacts(reacts):
            react_error = False
            at_least_one = False
            if None in reacts:
                nitro_error = True
            else:
                nitro_error = False

            for react in reacts:
                if isinstance(react, discord.Emoji):
                    try:
                        await ctx.message.add_reaction(react)
                        at_least_one = True
                    except Exception:
                        react_error = True

                elif isinstance(react, str):
                    string_options = (react, react[0:2], react[0])
                    for option in string_options:
                        try:
                            await ctx.message.add_reaction(option)
                            at_least_one = True
                            break
                        except Exception:
                            pass

            if react_error:
                print(f"{colors.RED_B}!vote{colors.CYAN} Not allowed to " +
                      f"add react in {ctx.guild.name}{colors.RESET}")
                await ctx.send(f"{ctx.author.mention} The moderators dun " +
                               "goofed I think. I encountered some sort of " +
                               "anomaly when trying to vote.")
            elif nitro_error:
                await ctx.send(f"{ctx.author.mention} There seem to be some " +
                               "emoji there I don't have access to.\nI need " +
                               "to be in the server the emoji is from.")
            elif not at_least_one:
                await ctx.send(f"{ctx.author.mention} There's literally " +
                               "nothing I can vote for you little " +
                               "smudmeister!")

        rows = ctx.message.content.split("\n")
        rows[0] = rows[0].replace("!vote ", "")
        reacts = [find_custom_emoji(row) for row in rows]
        await add_reacts(reacts)

    @discord.ext.commands.command(name="activity",
                                  aliases=["listen", "listening",
                                           "playing", "play",
                                           "game", "gaming", "gameing",
                                           "stream", "streaming",
                                           "watch", "watching"])
    # @discord.ext.commands.cooldown(1, (60*10), BucketType.default)
    async def _activity(self, ctx, *args):
        """Dictate what text should be displayed under my nick."""
        # Dictionary of all different activity types with keywords.
        # The keywords are defined in separate tuples so I can access
        # them without the dictionary.
        play_words = ("play", "playing", "game", "gaming", "gameing")
        stream_words = ("stream", "streaming")
        listen_words = ("listen", "listening")
        watch_words = ("watch", "watching")

        activity_types = {
            None: ("activity",),
            discord.ActivityType.playing: play_words,
            discord.ActivityType.streaming: stream_words,
            discord.ActivityType.listening: listen_words,
            discord.ActivityType.watching: watch_words
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
        if chosen_activity is None:
            for activity in activity_types:
                for alias in activity_types[activity]:
                    without_is = len(args) >= 1 and (args[0] == alias)
                    with_is = (len(args) >= 2) and (args[0:2] == ("is", alias))
                    if without_is:
                        chosen_activity = activity
                        args = args[1:]

                    elif with_is:
                        chosen_activity = activity
                        args = args[2:]

        success = False
        max_activity_length = 30
        if len(args) != 0:
            joint_args = ' '.join(args)

            # If we haven't been able to identify an
            # activity we'll default to listening.
            if chosen_activity is None:
                chosen_activity = discord.ActivityType.listening

            if len(joint_args) <= max_activity_length:
                try:
                    activity_obj = discord.Activity(
                        name=joint_args,
                        type=chosen_activity)
                    await self.bot.change_presence(activity=activity_obj)
                    success = True
                except Exception:
                    pass

        if chosen_activity == discord.ActivityType.playing:
            reply_activity = "playing"
        elif chosen_activity == discord.ActivityType.streaming:
            # streaming doesn't work as I want it,
            # always says playing not streaming.
            reply_activity = "playing"
        elif chosen_activity == discord.ActivityType.listening:
            reply_activity = "listening to"
        elif chosen_activity == discord.ActivityType.watching:
            reply_activity = "watching"
        else:
            # Default activity.
            reply_activity = "listening to"

        if success:
            await ctx.send(f"{ctx.author.mention} OK then, I guess I'm " +
                           f"**{reply_activity} {joint_args}** now.")

        elif len(args) == 0:
            # No activity specified.
            if chosen_activity is None:
                await ctx.send(f"{ctx.author.mention} " +
                               "You didn't tell me what to do.")

            else:
                # No name specified.
                await ctx.send(f"{ctx.author.mention} I can tell you want " +
                               f"me to be **{reply_activity}** something, " +
                               "but I don't know what.")

        elif len(joint_args) >= max_activity_length:
            # Too long.
            await ctx.send(f"{ctx.author.mention} That activity is stupidly " +
                           f"long ({len(joint_args)}). The limit is " +
                           f"{max_activity_length} characters.")

        else:
            await ctx.send("<@!154516898434908160> Something went wrong " +
                           "when trying to change my activity and I have no " +
                           "idea what. Come see!")
