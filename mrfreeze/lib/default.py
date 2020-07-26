"""Various standard methods to ensure consistent behaviour throughout application."""
from typing import Iterable
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


def word_distance(a: str, b: str) -> int:
    """Get the word distance between two words."""
    arr = [ [ 0 for x in range(len(b)) ] for y in range(len(a)) ]
    for x in range(0, len(a)):
        arr[x][0] = x
    for x in range(0, len(b)):
        arr[0][x] = x
    for row in range(1, len(a)):
        for col in range(1, len(b)):
            if a[row] == b[col]:
                cost = 0
            else:
                cost = 1
    arr[row][col] = min(
        1 + arr[row - 1][col],
        1 + arr[row][col - 1],
        cost + arr[row - 1][col - 1])

    return arr[len(a) - 1][len(b) - 1]


def get_closest_match(candidates: Iterable[str], input: str) -> str:
    """
    Get the closest matching string from a list of candidates.

    This method acts as a wrapper for word distance.
    """
    return min(candidates, key=lambda k: word_distance(k, input))
