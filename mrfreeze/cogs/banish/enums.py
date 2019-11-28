from enum import Enum, auto         # Used for the templates dictionary


# Templates for the various responses. There are lots of them.
class MuteType(Enum):
    MUTE: str = "muted"
    BANISH: str = "banished"
    HOGTIE: str = "hogtied"


class MuteStr(Enum):
    """Various categories of !mute attempts."""
    # MrFreeze
    FREEZE = auto()          # Tried muting: MrFreeze
    FREEZE_SELF = auto()     # Tried muting: MrFreeze + only self
    FREEZE_OTHERS = auto()   # Tried muting: MrFreeze + others (possibly self)
    # Mod mutes (any added users will just be ignored for simplicity)
    SELF = auto()            # Tried muting: self
    MOD = auto()             # Tried muting: a single mod
    MODS = auto()            # Tried muting: several mods (possibly self)
    # At user mutes (mods muting users)
    NONE = auto()            # No mentions in list
    SINGLE = auto()          # Successfully muted one
    MULTI = auto()           # Successfully muted more than one
    FAIL = auto()            # Failed to mute one
    FAILS = auto()           # Failed to mute more than one
    SINGLE_FAIL = auto()     # Muted one, failed one
    SINGLE_FAILS = auto()    # Muted one, failed multiple
    MULTI_FAIL = auto()      # Muted multiple, failed one
    MULTI_FAILS = auto()     # Muted multiple, failed multiple
    # Unmutes
    INVALID = auto()         # Invalid unmute (targeting freeze or mods)
    UNSINGLE = auto()        # Successfully unmuted one
    UNMULTI = auto()         # Successfully unmuted more than one
    UNFAIL = auto()          # Failed to unmute one
    UNFAILS = auto()         # Failed to unmute more than one
    UNSINGLE_FAIL = auto()   # Unmuted one, failed one
    UNSINGLE_FAILS = auto()  # Unmuted one, failed multiple
    UNMULTI_FAIL = auto()    # Unmuted multiple, failed one
    UNMULTI_FAILS = auto()   # Unmuted multiple, failed multiple
    # By user mutes (users trying to mute)
    USER_NONE = auto()       # User invoked mute with no arguments
    USER_SELF = auto()       # User tried muting themselves
    USER_USER = auto()       # User tried muting other user(s)
    USER_MIXED = auto()      # User tried musing themselves and other user(s)
    USER_FAIL = auto()       # User punishment failed
    # Timestamp
    TIMESTAMP = auto()       # The time stamp for the end of the message
