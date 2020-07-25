"""Various standard methods to ensure consistent behaviour throughout application."""
from typing import List

from discord import User


def mentions_list(mentions: List[User]) -> str:
    """Create a string of mentions from a list of user objects."""
    mentions = [user.mention for user in mentions]
    if len(mentions) == 0:
        return "No one"
    elif len(mentions) == 1:
        return mentions[0]
    else:
        return ", ".join(mentions[:-1]) + f" and {mentions[-1]}"
