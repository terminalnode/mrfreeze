"""Module for functions used by !whois/!whoami, sends a message with user info."""

from typing import List
from typing import Optional

from discord import Embed
from discord import Member
from discord.ext.commands import Context


async def run(ctx: Context) -> None:
    """Run the server info command."""
    if not ctx.message.mentions or ctx.invoked_with == "whoami":
        await ctx.send(embed=get_user_info(ctx, ctx.author))
    else:
        await ctx.send(embed=get_user_info(ctx, ctx.message.mentions[0]))


def get_user_info(ctx: Context, member: Member) -> Embed:
    """Fetch information about a user and put it in an Embed."""
    embed = Embed(color=0x00dee9)
    embed.title = f"{member} information"
    add_thumbnail(member, embed)

    if ctx.guild:
        # Include guild info
        add_user_roles(member, embed, 10)
        add_permissions_in_channel(ctx, member, embed)
        add_joined_server_at(member, embed)
        add_account_created_at(member, embed)

    else:
        # Do not include guild info
        add_account_created_at(member, embed)

    return embed


def add_thumbnail(member: Member, embed: Embed) -> None:
    """Add the users avatar as a thumbnail to embed."""
    if member.avatar:
        format = "gif" if member.is_avatar_animated() else "png"
        embed.set_thumbnail(url=member.avatar_url_as(format=format))


def add_user_roles(member: Member, embed: Embed, limit: Optional[int] = None) -> None:
    """Add a list of the user's roles to embed."""
    role_mentions = "None"
    roles = member.roles[1:]  # Get rid of the everyone role

    if roles:
        if limit:
            roles = roles[:limit]
        roles.reverse
        role_mentions = "\n".join([r.mention for r in roles])

    embed.add_field(name="Roles", value=role_mentions)


def add_joined_server_at(member: Member, embed: Embed) -> None:
    """Add information on when the member joined."""
    time = member.joined_at

    if time:
        text = time.strftime("%Y-%m-%d %H:%M")
    else:
        # In some cases time can be None.
        text = "Unknown 😨"

    embed.add_field(name="Join server", value=text)


def add_account_created_at(member: Member, embed: Embed) -> None:
    """Add the date when the accound was created to embed."""
    time = member.created_at.strftime("%Y-%m-%d %H:%M")
    embed.add_field(name="Account created", value=time)


def add_permissions_in_channel(ctx: Context, member: Member, embed: Embed) -> None:
    """Add what permissions the user has in the current channel."""
    p = member.permissions_in(ctx.channel)
    yes = "✅"
    no = "🚫"
    text: List[str] = [ ]

    if p.administrator:
        # They're an admin, no need to write out everything they can do.
        text.append("👑 Administrator 👑")

    else:
        # For other permissions, we'll split them into groups to reduce size.
        # Permissions are extracted from permissions beforehand to help detect attribute errors.
        they_kick = p.kick_members
        they_ban = p.ban_members
        if they_kick and they_ban:
            text.append(f"{yes} Kick and ban members")
        elif they_ban:
            text.append(f"{yes} Ban members")
        elif they_kick:
            text.append(f"{yes} Kick members")
        else:
            text.append(f"{no} Kick or ban members")

        manage_channels = p.manage_channels
        manage_guild = p.manage_guild
        if manage_channels and manage_guild:
            text.append(f"{yes} Manage guild and channels")
        elif manage_channels:
            text.append(f"{yes} Manage channels")
        elif manage_guild:
            text.append(f"{yes} Manage guild")
        else:
            text.append(f"{no} Manage guild or channels")

        manage_perms = p.manage_permissions
        manage_emoji = p.manage_emojis
        if manage_perms and manage_emoji:
            text.append(f"{yes} Manage guild permissions and emoji")
        elif manage_perms:
            text.append(f"{yes} Manage guild permissions")
        elif manage_emoji:
            text.append(f"{yes} Manage guild emoji")
        else:
            text.append(f"{no} Manage guild permissions or emoji")

        send = p.send_messages
        manage = p.manage_messages
        react = p.add_reactions
        if send and manage and react:
            text.append(f"{yes} Send, delete, pin and react to messages")
        elif send and manage:
            text.append(f"{yes} Send, delete and pin messages")
        elif send and react:
            text.append(f"{yes} Send and react to messages")
        elif manage and react:
            text.append(f"{yes} Delete, pin and react to messages")
        elif manage:
            text.append(f"{yes} Delete and pin messages")
        elif send:
            text.append(f"{yes} Send messages")
        elif react:
            text.append(f"{yes} React to messages")
        else:
            text.append(f"{no} Send, delete, pin or react to messages")

        check_voicemod = True
        connect = p.connect
        speak = p.speak
        priority = p.priority_speaker
        if connect and speak and priority:
            text.append(f"{yes} Is a priority speaker in voice")
        elif connect and speak:
            text.append(f"{yes} Speak in voice")
        elif connect:
            text.append(f"{yes} Connect to voice")
        else:
            text.append(f"{no} Participate in voice")
            check_voicemod = False

        # Checking voicemod permissions.
        # Only relevant if users can connect to voice, hence check_voicemod.
        if check_voicemod:
            move = p.move_members
            mute = p.mute_members
            deafen = p.deafen_members

            if move and mute and deafen:
                text.append(f"{yes} Moderate voice")
            elif move and mute:
                text.append(f"{yes} Move and mute members in voice")
            elif mute and deafen:
                text.append(f"{yes} Mute and deafen members in voice")
            elif move and deafen:
                text.append(f"{yes} Move and deafen members in voice")
            elif move:
                text.append(f"{yes} Move members in voice")
            elif mute:
                text.append(f"{yes} Mute members in voice")
            elif deafen:
                text.append(f"{yes} Deafen members in voice")
            else:
                text.append(f"{no} Moderate voice")

    embed.add_field(name="Permissions", value="\n".join(text))
