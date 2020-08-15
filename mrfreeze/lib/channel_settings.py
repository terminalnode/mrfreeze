"""A module for changing various settings in the bot."""

from enum import Enum
from enum import auto

from discord import Guild
from discord import TextChannel


class ChannelReturnType(Enum):
    """An enum to distinguish between different types of channels."""

    WELCOME = auto()
    LEAVE   = auto()
    SYSMSG  = auto()
    MUTE    = auto()
    TRASH   = auto()


class TypedChannel:
    """A class for packaging a TextChannel with it's associated ChannelType."""

    channel: TextChannel
    type: ChannelReturnType
    desired_type: ChannelReturnType

    def __init__(self, channel: TextChannel, type: ChannelReturnType, desired_type: ChannelReturnType) -> None:
        self.channel = channel
        self.type = type
        self.desired_type = desired_type

    def get_mention(self, skip_explanation: bool = False) -> str:
        """
        Get a string with a mention of the channel.

        If the desired type is the same as the actual type, only a mention of the channel is returned.
        If not, a short parenthesised explanation is included after the mention.
        """
        if skip_explanation or self.type == self.desired_type:
            return self.channel.mention

        elif self.type == ChannelReturnType.SYSMSG:
            return f"{self.channel.mention} (the system messages channel)"

        elif self.type == ChannelReturnType.WELCOME:
            return f"{self.channel.mention} (the channel for welcome messages)"

        elif self.type == ChannelReturnType.LEAVE:
            return f"{self.channel.mention} (the channel for leave messages)"

        elif self.type == ChannelReturnType.MUTE:
            return f"{self.channel.mention} (the mute/banish channel)"

        elif self.type == ChannelReturnType.TRASH:
            return f"{self.channel.mention} (the server's trash channel)"

        else:
            return self.channel.mention

    def __str__(self) -> str:
        """
        Get a string representing the channel.

        If the desired type is the same as the actual type, only a mention of the channel is returned.
        If not, a short parenthesised explanation is included after the mention.
        """
        return self.get_mention(skip_explanation=False)


async def set_mute_channel(guild: Guild, channel: TextChannel) -> None:
    """Set the mute channel for a given server."""
    raise NotImplementedError()  # TODO


async def set_trash_channel(guild: Guild, channel: TextChannel) -> None:
    """Set the trash channel for a given server."""
    raise NotImplementedError()  # TODO


async def set_welcome_channel(guild: Guild, channel: TextChannel) -> None:
    """Set the welcome channel for a given server."""
    raise NotImplementedError()  # TODO


async def set_leave_channel(guild: Guild, channel: TextChannel) -> None:
    """Set the leave channel for a given server."""
    raise NotImplementedError()  # TODO
