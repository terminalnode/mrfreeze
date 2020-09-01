"""Module for functions used by !server."""

import datetime

from discord import Embed
from discord import TextChannel
from discord.ext.commands import Context

from mrfreeze.database.settings import Settings
from mrfreeze.lib import welcome_messages
from mrfreeze.lib import leave_messages


async def run(ctx: Context) -> None:
    """Run the !server command."""
    if ctx.guild:
        await ctx.send(embed= await create_embed(ctx))
    else:
        await ctx.send(f"{ctx.author.mention} Don't be silly.")


async def create_embed(ctx: Context) -> Embed:
    """Create the embed for the command."""
    embed = Embed(color=0x00dee9)
    embed.title = f"{ctx.guild.name} server information"
    add_thumbnail(ctx, embed)
    add_owner_field(ctx, embed)
    add_region_field(ctx, embed)
    add_system_channel_field(ctx, embed)
    add_verification_level_field(ctx, embed)
    add_custom_emoji_field(ctx, embed)
    add_roles_field(ctx, embed)
    add_freeze_features(ctx, embed)
    add_channels_field(ctx, embed)
    add_members_field(ctx, embed)
    await add_welcome_channel_field(ctx, embed)
    await add_leave_channel_field(ctx, embed)
    add_footer(ctx, embed)
    return embed


def add_thumbnail(ctx: Context, embed: Embed) -> None:
    """Add server icon as thumbnail to embed, if there is one."""
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))


def add_owner_field(ctx: Context, embed: Embed) -> None:
    """Add owner field to embed."""
    owner = ctx.guild.owner
    if owner:
        embed.add_field(name="Owner", value=owner.mention)


def add_region_field(ctx: Context, embed: Embed) -> None:
    """Add region field to embed."""
    region = ctx.guild.region
    if region:
        embed.add_field(name="Region", value=region)


def add_system_channel_field(ctx: Context, embed: Embed) -> None:
    """Add system channel field to embed."""
    sys_channel = ctx.guild.system_channel
    if isinstance(sys_channel, TextChannel):
        embed.add_field(name="Main channel", value=sys_channel.mention)


def add_verification_level_field(ctx: Context, embed: Embed) -> None:
    """Add verification level field to embed."""
    embed.add_field(name="Verification level", value=ctx.guild.verification_level)


def add_custom_emoji_field(ctx: Context, embed: Embed) -> None:
    """Add custom emoji field to embed."""
    emoji_limit = ctx.guild.emoji_limit
    emoji = ctx.guild.emojis
    animated_emoji = len([ e for e in emoji if e.animated ])
    static_emoji = len(emoji) - animated_emoji

    text = f"Regular: {static_emoji}\n"
    text += f"Animated: {animated_emoji}\n"
    text += f"Max: {emoji_limit}"
    embed.add_field(name="Custom emoji", value=text)


def add_roles_field(ctx: Context, embed: Embed) -> None:
    """Add roles field to embed."""
    embed.add_field(name="Roles", value=len(ctx.guild.roles))


def add_members_field(ctx: Context, embed: Embed) -> None:
    """Add members field to embed."""
    members = ctx.guild.members
    bots = len([ m for m in members if m.bot ])
    mods = len([ m for m in members if m.guild_permissions.administrator ])
    members_text = f"Boterators: {bots}\n"
    members_text += f"Moderators: {mods}\n"
    members_text += f"Smuds: {len(members) - bots - mods}"

    embed.add_field(name="Members", value=members_text)


def add_channels_field(ctx: Context, embed: Embed) -> None:
    """Add channels field to embed."""
    channels = len(ctx.guild.channels)
    text_channels = len(ctx.guild.text_channels)
    voice_channels = len(ctx.guild.voice_channels)
    channels_text = f"Text: {text_channels}\n"
    channels_text += f"Voice: {voice_channels}\n"
    channels_text += f"Total: {channels}"

    embed.add_field(name="Channels", value=channels_text)


def add_freeze_features(ctx: Context, embed: Embed) -> None:
    """Add MrFreeze features field to embed."""
    features = list()
    settings: Settings = ctx.bot.settings
    yes = "✅"
    no = "🚫"

    # Check if inkbot is enabled
    if settings.is_inkcyclopedia_muted(ctx.guild):
        features.append(f"{no} Inkcyclopedia")
    else:
        features.append(f"{yes} Inkcyclopedia")

    if settings.is_tempconverter_muted(ctx.guild):
        features.append(f"{no} Temp conversion")
    else:
        features.append(f"{yes} Temp conversion")

    feature_list = "\n".join(features)
    embed.add_field(name="MrFreeze features", value=feature_list)


def add_footer(ctx: Context, embed: Embed) -> None:
    """Add footer displaying the server creation date to embed."""
    created = ctx.guild.created_at
    days_ago = (datetime.datetime.now() - created).days
    created_str = created.strftime("%Y-%m-%d")

    embed.set_footer(text=f"Created {created_str}  |  {days_ago} days ago")

async def add_welcome_channel_field(ctx: Context, embed: Embed) -> None:
    """Add Welcome channel field to the embed"""
    welcome_channel = await welcome_messages.get_welcome_channel(ctx.guild, ctx.bot)
    embed.add_field(name="Welcome Channel", value=welcome_channel.get_mention(True))

async def add_leave_channel_field(ctx: Context, embed: Embed) -> None:
    """Add Leave channel field to the embed"""
    leave_channel = await leave_messages.get_leave_channel(ctx.guild, ctx.bot)
    embed.add_field(name="Leave Channel", value=leave_channel.get_mention(True))