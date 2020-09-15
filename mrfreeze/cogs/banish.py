"""
Banish cog.

This cog is for the banish/mute command and the region command.
banish/mute is closely connected to the region command since
they both use the antarctica mechanics.

Therefor they're both in a cog separate from everything else.
"""

import logging
from typing import Dict
from typing import List
from typing import Optional

import discord
from discord import Member
from discord.ext.commands import Cog
from discord.ext.commands import Context
from discord.ext.commands import command

from mrfreeze.bot import MrFreeze
from mrfreeze.cogs.coginfo import CogInfo
from mrfreeze.lib import checks
from mrfreeze.lib import region
from mrfreeze.lib.banish import banish
from mrfreeze.lib.banish import banish_time
from mrfreeze.lib.banish import mute_db
from mrfreeze.lib.banish import templates as banish_templates
from mrfreeze.lib.banish import time_settings
from mrfreeze.lib.banish import unauthorized_banish
from mrfreeze.lib.banish.roulette import roulette
from mrfreeze.lib.banish.unbanish_loop import unbanish_loop

mute_templates: banish_templates.TemplateEngine
template_engine = banish_templates.TemplateEngine()

mute_command: str
mute_command_aliases: List[str]
(mute_command, *mute_command_aliases) = template_engine.get_aliases()

selfmute_command = "selfmutetime"
selfmute_aliases = ['smt', 'selfmute', 'mutetime']

banish_interval_command = "banishinterval"
banish_interval_aliases = [ "muteinterval" ]

banishtime_command = "banishtime"
banishtime_aliases = [ "amibanished", "howmuchlonger" ]


def setup(bot: MrFreeze) -> None:
    """Load the cog into the bot."""
    bot.add_cog(BanishAndRegion(bot))


class BanishAndRegion(Cog):
    """Good mod! Read the manual! Or if you're not mod - sod off."""

    def __init__(self, bot: MrFreeze) -> None:
        self.bot = bot
        self.regions: Dict[int, Dict[str, Optional[int]]] = dict()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.default_mute_interval = 5
        self.default_self_mute_time = 20

        self.coginfo = CogInfo(self)

        mute_db.create_table(self.bot)

    @Cog.listener()
    async def on_ready(self) -> None:
        """
        Once ready, do some setup for all servers.

        This is mostly stuff pertaining to banishes and regions, such as setting up the periodic
        unbanish and indexing all the servers' regional roles.
        """
        for server in self.bot.guilds:
            # Add unbanish loop to bot
            self.bot.add_bg_task(unbanish_loop(server, self.coginfo), f'unbanish@{server.id}')

            # Construct region dict
            self.regions[server.id] = dict()
            for region_name in region.regional_aliases.keys():
                region_role = discord.utils.get(server.roles, name=region_name)
                if region_role:
                    self.regions[server.id][region_name] = region_role.id
                else:
                    self.regions[server.id][region_name] = None

    @command(name=banish_interval_command, aliases=banish_interval_aliases)
    @discord.ext.commands.check(checks.is_owner_or_mod)
    async def _banishinterval(self, ctx: Context, interval: Optional[int]) -> None:
        await time_settings.set_banish_interval(ctx, self.bot, interval)

    @command(name=selfmute_command, aliases=selfmute_aliases)
    @discord.ext.commands.check(checks.is_owner_or_mod)
    async def _selfmutetime(self, ctx: Context, number: Optional[int]) -> None:
        await time_settings.set_self_mute(ctx, self.bot, number)

    @command(name=mute_command, aliases=mute_command_aliases)
    @discord.ext.commands.check(checks.is_mod_silent)
    async def _banish(self, ctx: Context, *args: str) -> None:
        """Mute one or more users (can only be invoked by mods)."""
        await banish.run_command(ctx, self.coginfo, template_engine, args)

    @_banish.error
    async def unauthorized_banish(self, ctx: Context, error: Exception) -> None:
        """Trigger automatically when _banish throws an error, and punish the user."""
        await unauthorized_banish.run_command(ctx, self.coginfo, template_engine, error)

    @command(name=banishtime_command, aliases=banishtime_aliases)
    async def banishtime(self, ctx: Context, user: Optional[Member]) -> None:
        """Check how long until you're unbanished."""
        await banish_time.run_command(ctx, self.coginfo, user)

    @command(name="roulette")
    async def roulette(self, ctx: Context) -> None:
        """Roll the dice and test your luck, banish or nothing."""
        await roulette(ctx, self.coginfo)

    @command(name="region", aliases=["regions"])
    async def _region(self, ctx: Context, *args: str) -> None:
        """Assign yourself a colourful regional role."""
        await region.region_cmd(ctx, self.coginfo, args)
