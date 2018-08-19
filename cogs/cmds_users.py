import discord, re
from discord.ext import commands
from botfunctions import native

class RulesCog():
    def __init__(self, bot):
        self.bot = bot

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
        6: ( '6', 'spam' ),
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
            await ctx.send('Sorry %s, your terms don\'t seem to match any rules. :thinking:' % (ctx.author.mention,))
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
            await ctx.send('Allow me to break the ice: My name is Freeze and ' +
            'the command **!mrfreeze** will have me print one of my timeless quotes from Batman & Robin.')
        elif suck_reply:
            await ctx.send('Freeze in hell, ' + ctx.author.mention + '!')
        elif death_reply:
            await ctx.send(ctx.author.mention + ' ' +
            'You\'re not sending ME to the COOLER!')
        else:
            quote = native.mrfreeze()
            quote = quote.replace('Batman', ctx.author.mention)
            quote = quote.replace('Gotham', '**' + ctx.guild.name + '**')
            await ctx.send(quote)

    @commands.command(name='vote', aliases=['election', 'choice', 'choose'])
    async def _vote(self, ctx, *args):
        remoji = re.compile('<:\w+:\d+>')
        remojid = re.compile('\d+')
        # skipping first line because we don't need it
        lines = ctx.message.content.split()[1:]

        # For each line we'll try to add a react of the first character,
        # if that fails we'll look for a custom emoji of the form:
        # <:\w+:\d+> (remoji)

        success = False
        for line in lines:
            try:
                await ctx.message.add_reaction(line[0])
                success = True
            except:
                pass

            match = remoji.match(line)
            if not isinstance(match, type(None)):
                match_id = int(remojid.search(match.group()).group())
                emoji = discord.utils.get(ctx.guild.emojis, id=match_id)
                try:
                    await ctx.message.add_reaction(emoji)
                    success = True
                except:
                    pass

        if success:
            await ctx.send('%s That\'s such a great proposition I voted for everything!' % (ctx.author.mention))
        else:
            await ctx.send('%s There\'s literally nothing I can vote for in your so-called "vote"! :rofl:' % (ctx.author.mention,))


def setup(bot):
    bot.add_cog(RulesCog(bot))
