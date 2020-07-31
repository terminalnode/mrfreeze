"""Module for handling automatic unbanishments."""
import asyncio
import datetime
from logging import Logger

from discord import Guild

from mrfreeze.bot import MrFreeze
from mrfreeze.cogs.coginfo import CogInfo
from mrfreeze.lib import default
from mrfreeze.lib.banish import mute_db
from mrfreeze.lib.colors import CYAN
from mrfreeze.lib.colors import CYAN_B
from mrfreeze.lib.colors import MAGENTA
from mrfreeze.lib.colors import RED
from mrfreeze.lib.colors import RESET
from mrfreeze.lib.colors import YELLOW


async def unbanish_loop(server: Guild, coginfo: CogInfo) -> None:
    """Check for people to unbanish every self.banish_interval seconds."""
    if coginfo.bot and coginfo.logger and coginfo.default_mute_interval:
        bot: MrFreeze = coginfo.bot
        logger: Logger = coginfo.logger
        default_mute_interval: int = coginfo.default_mute_interval
    else:
        raise Exception("Failed to create unbanish loop, insufficient cog info.")

    while not bot.is_closed():
        # Wait the time specified by the server (or the default time) before running
        interval = bot.settings.get_mute_interval(server) or default_mute_interval
        logger.debug(f"Running unbanish loop for {server.name} in {interval}.")
        await asyncio.sleep(interval)
        logger.debug(f"Running unbanish loop for {server.name}.")

        # Fetch mute role/channel, which might fail.
        try:
            mute_role = await bot.get_mute_role(server)
            mute_channel = await bot.get_mute_channel(server, silent=True)
        except Exception:
            logger.warning(f"{server.name} Unbanish loop failed to fetch mute role or channel.")
            continue
        unmuted = list()

        # Create a list of mutes which are due for unmuting
        current_time = datetime.datetime.now()
        mutes = mute_db.mdb_fetch(bot, server)
        timed_mutes = [ i for i in mutes if i.until is not None ]
        due_mutes = [ i for i in timed_mutes if i.until < current_time ]
        logger.debug(f"{server.name} mutes: {len(mutes)}/{len(timed_mutes)}/{len(due_mutes)}")

        for mute in due_mutes:
            logger.debug(f"{mute} is due for unbanish!")

            # Refresh member to make sure we have their latest roles.
            try:
                member = await server.fetch_member(mute.member.id)
                logger.debug(f"Refreshed {member}, they have {len(member.roles)} roles.")
            except Exception as e:
                logger.error(f"Failed to refresh muted member: {e}")
                continue  # Will try again next unbanish loop

            # Calculate how late we were in unbanishing
            diff = bot.parse_timedelta(current_time - mute.until)
            if diff == "":
                diff = "now"
            else:
                diff = f"{diff} ago"

            # Remove from database
            mute_db.mdb_del(bot, member, logger)

            if mute_role in member.roles:
                logger.debug(f"{member} has the mute role! Removing it.")
                try:
                    await member.remove_roles(mute_role)
                    logger.debug(f"{member} should no longer have the mute role.")
                    # Members are only considered unmuted if they had the antarctica role
                    unmuted.append(member)

                    log = f"Auto-unmuted {CYAN_B}{member.name}#"
                    log += f"{member.discriminator} @ {server.name}."
                    log += f"{YELLOW} (due {diff}){RESET}"
                    logger.info(log)

                except Exception as e:
                    log = f"Failed to remove mute role of {YELLOW}"
                    log += f"{member.name}#{member.discriminator}"
                    log += f"{CYAN_B} @ {MAGENTA} {server.name}:"
                    log += f"\n{RED}==> {RESET}{e}"
                    logger.error(log)
            else:
                log = f"User {YELLOW}{member.name}#{member.discriminator}"
                log += f"{CYAN_B} @ {MAGENTA} {server.name}{CYAN} "
                log += f"due for unmute but does not have a mute role!{RESET}"
                logger.warning(log)

        # Time for some great regrets
        if len(unmuted) > 0:
            unmuted_str = default.mentions_list(unmuted)

            if len(unmuted_str) == 1:
                msg = "It's with great regret that I must inform you all that "
                msg += f"{unmuted_str}'s exile has come to an end."
            else:
                msg = "It's with great regret that I must inform you all that the exile of "
                msg += f"{unmuted_str} has come to an end."

            await mute_channel.send(msg)
