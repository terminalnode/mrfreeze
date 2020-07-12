"""Module for reading the string template responses for banish."""

import itertools
from enum import Enum
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import MutableMapping

import toml


class DuplicateAliasException(Exception):
    """Exception used when one or more of the aliases already exist."""


class MissingNameException(Exception):
    """Exception used when one or more of the aliases already exist."""


class MuteResponse(Enum):
    """Various categories of !mute attempts/results."""

    FREEZE          = "freeze"          # Tried muting: MrFreeze
    FREEZE_SELF     = "freeze_self"     # Tried muting: MrFreeze + only self
    FREEZE_OTHERS   = "freeze_others"   # Tried muting: MrFreeze + others (possibly self)
    SELF            = "self"            # Tried muting: self
    MOD             = "mod"             # Tried muting: a single mod
    MODS            = "mods"            # Tried muting: several mods (possibly self)
    NONE            = "none"            # No mentions in list
    SINGLE          = "single"          # Successfully muted one
    MULTI           = "multi"           # Successfully muted more than one
    FAIL            = "fail"            # Failed to mute one
    FAILS           = "fails"           # Failed to mute more than one
    SINGLE_FAIL     = "single_fail"     # Muted one, failed one
    SINGLE_FAILS    = "single_fails"    # Muted one, failed multiple
    MULTI_FAIL      = "multi_fail"      # Muted multiple, failed one
    MULTI_FAILS     = "multi_fails"     # Muted multiple, failed multiple
    INVALID         = "invalid"         # Invalid unmute (targeting freeze or mods)
    UNSINGLE        = "unsingle"        # Successfully unmuted one
    UNMULTI         = "unmulti"         # Successfully unmuted more than one
    UNFAIL          = "unfail"          # Failed to unmute one
    UNFAILS         = "unfails"         # Failed to unmute more than one
    UNSINGLE_FAIL   = "unsingle_fail"   # Unmuted one, failed one
    UNSINGLE_FAILS  = "unsingle_fails"  # Unmuted one, failed multiple
    UNMULTI_FAIL    = "unmulti_fail"    # Unmuted multiple, failed one
    UNMULTI_FAILS   = "unmulti_fails"   # Unmuted multiple, failed multiple
    USER_NONE       = "user_none"       # User invoked mute with no arguments
    USER_SELF       = "user_self"       # User tried muting themselves
    USER_USER       = "user_user"       # User tried muting other user(s)
    USER_MIXED      = "user_mixed"      # User tried musing themselves and other user(s)
    USER_FAIL       = "user_fail"       # User punishment failed
    TIMESTAMP       = "timestamp"       # The time stamp for the end of the message


files = [
    "mute.toml", "banish.toml", "hogtie.toml"
]


def load_files(skip_alias: str = "mute") -> Dict[str, Any]:
    """
    Load all files.

    The skip aliases is an alias that should be skipped. The default value for this is
    'mute' because that's the main name of the command, and thus can't be an alias.
    """
    all_files: Dict[str, Any] = dict()
    all_files["aliases"] = list()

    for file in files:
        data: MutableMapping[str, Any] = toml.load(f"config/banish_templates/{file}")
        add_aliases(data, file, all_files["aliases"], skip_alias)

    return all_files


def add_aliases(data: MutableMapping[str, Any], filename: str, all: List[str], skip: str) -> None:
    """Process names from the template."""
    names = data.get("names")
    if not names:
        raise MissingNameException(f"{filename} is missing names section")

    main_name = strip_iterable(names.get("main"))
    undo_name = strip_iterable(names.get("undo"))
    micro_name = strip_iterable(names.get("micro"))
    super_name = strip_iterable(names.get("super"))
    mega_name = strip_iterable(names.get("mega"))

    # micro/super/mega will be added later if they exist
    aliases = [ main_name, undo_name ]

    if not data.get("names", "main"):
        raise MissingNameException(f"{filename} is missing names => main")
    elif not data.get("names", "undo"):
        raise MissingNameException(f"{filename} is missing names => undo")

    for name in [micro_name, super_name, mega_name]:
        if name:
            aliases.append(name)
    flat_aliases = list(itertools.chain.from_iterable(aliases))

    # Add aliases to `all`, if they're not already in there.
    for alias in flat_aliases:
        print(alias)
        if alias == skip:
            continue
        if alias not in all:
            all.append(alias)
        else:
            raise DuplicateAliasException(f"Can't add alias {alias} from {filename}.")


def strip_iterable(iterable: Iterable) -> Iterable:
    """Remove all empty strings from an iterable."""
    if iterable:
        return [ i for i in iterable if isinstance(i, str) and i ]
    else:
        return iterable
