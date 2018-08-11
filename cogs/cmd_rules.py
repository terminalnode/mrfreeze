import discord
from discord.ext import commands
from botfunctions import native

class RulesCog():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='rules', aliases=['rule'])
    async def _rules(self, ctx, *args):
        request = str()
        for i in args:
            request += (i)

        rules = {
        1: ( '1', 'topic', 'ontopic', 'offtopic' ),
        2: ( '2', 'civil', 'disagreement' ),
        3: ( '3', 'dismissive', 'opinion', 'opinions' ),
        4: ( '4', 'joke', 'jokes', 'joking', 'sex', 'sexual', 'orientation', 'weight', 'race' ),
        5: ( '5', 'shoe', 'shoes', 'age', 'mature', 'maturity', 'shoesize' ),
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
                    if keyword in args and rule_no not in called_rules:
                        called_rules.append(rule_no)

        await ctx.send(native.get_rule(called_rules))

def setup(bot):
    bot.add_cog(RulesCog(bot))
