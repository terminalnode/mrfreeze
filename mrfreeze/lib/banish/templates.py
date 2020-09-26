"""Module for reading the string template responses for banish."""

import itertools
from enum import Enum
from enum import auto
from string import Template
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import MutableMapping
from typing import Optional

import toml


# List of all the template files that should be loaded.
files = [
    "mute.toml", "banish.toml", "hogtie.toml"
]


class DuplicateAliasException(Exception):
    """Exception used when one or more of the aliases already exist."""


class MissingNameException(Exception):
    """Exception used when a name that is required does not exist."""


class MissingTemplateException(Exception):
    """Exception used when one or more of the templates are missing.."""


class MuteResponseType(Enum):
    """Various categories of !mute attempts/results."""

    FREEZE          = "freeze"          # Tried muting: MrFreeze
    FREEZE_SELF     = "freeze_self"     # Tried muting: MrFreeze + only self
    FREEZE_OTHERS   = "freeze_others"   # Tried muting: MrFreeze + others (possibly self)
    FREEZE_OWNER    = "freeze_owner"    # Tried muting: bot owner
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


class MuteCommandType(Enum):
    """Various categories of !mute commands (undo, micro, mega, etc)."""

    MAIN    = auto()
    UNDO    = auto()
    MICRO   = auto()
    SUPER   = auto()
    MEGA    = auto()


class BanishTemplate:
    """Class for holding a single template."""

    data: MutableMapping[str, Any]
    filename: str
    names: List[str]
    names_main: List[str]
    names_undo: List[str]
    names_micro: List[str]
    names_super: List[str]
    names_mega: List[str]
    templates: Dict[MuteResponseType, Template]

    def __init__(self, file: str, others: List["BanishTemplate"]) -> None:
        self.data = toml.load(f"config/banish_templates/{file}")
        self.filename = file
        self.parse_names(others)
        self.parse_templates()

    def get_command_type(self, invocation: str) -> Optional[MuteCommandType]:
        """Return the appropriate MuteCommandType based on invocation used."""
        if invocation in self.names_main:
            return MuteCommandType.MAIN

        elif invocation in self.names_undo:
            return MuteCommandType.UNDO

        elif invocation in self.names_micro:
            return MuteCommandType.MICRO

        elif invocation in self.names_super:
            return MuteCommandType.SUPER

        elif invocation in self.names_mega:
            return MuteCommandType.MEGA

        return None

    def get_template(self, mute_response: MuteResponseType) -> Optional[Template]:
        """Return the appropriate template."""
        return self.templates[mute_response]

    def has_name(self, name: str) -> bool:
        """Check if this template has this name."""
        return name in self.names

    def has_any_name(self, names: List[str]) -> bool:
        """Check if this template has any name in the list."""
        return any([ name in self.names for name in names ])

    def parse_names(self, others: List['BanishTemplate']) -> None:
        """Read this template's command names from data."""
        # Verify that all the required fields are filled in,  add used fields to
        # unflattened_aliases and finally set self.names to this flattened list.
        names = self.data.get("names")
        if not names:
            raise MissingNameException(f"{self.filename} is missing names section.")

        self.names_main = self.strip_list(names.get("main"))
        self.names_undo = self.strip_list(names.get("undo"))
        self.names_micro = self.strip_list(names.get("micro"))
        self.names_super = self.strip_list(names.get("super"))
        self.names_mega = self.strip_list(names.get("mega"))

        if not self.names_main:
            raise MissingNameException(f"{self.filename} is missing names => main")
        elif not self.names_undo:
            raise MissingNameException(f"{self.filename} is missing names => undo")

        self.names = self.names_main + self.names_undo
        self.names += self.names_micro + self.names_super + self.names_mega

        # Check for duplicates
        for other in others:
            if not other.has_any_name(self.names):
                continue

            for name in self.names:
                if other.has_name(name):
                    error = f"Duplicate name {name} in {self.filename} and {other.filename}."
                    raise DuplicateAliasException(error)

    def parse_templates(self) -> None:
        """Read this template's template strings from data."""
        templates = self.data.get("templates")
        self.templates = dict()

        if not templates:
            error = f"{self.filename} is missing templates section."
            raise MissingTemplateException(error)

        for template in MuteResponseType:
            template_string = templates.get(template.value)
            if not template_string:
                error = f"{self.filename} is missing template: {template.value}"
                raise MissingTemplateException(error)

            self.templates[template] = Template(template_string)

    def strip_list(self, input: List) -> List:
        """Remove all empty strings from an iterable."""
        if input:
            return [ i for i in input if isinstance(i, str) and i ]
        else:
            return input

    def __repr__(self) -> str:
        return f"<BanishTemplate {self.filename}>"


class TemplateEngine:
    """Class for holding all templates."""

    templates: List[BanishTemplate]

    def __init__(self, files: Iterable[str] = files) -> None:
        self.templates = list()

        for file in files:
            new_template = BanishTemplate(file, self.templates)
            new_template.parse_names(self.templates)
            self.templates.append(new_template)

    def get_aliases(self) -> List[str]:
        """Get a list of all command names."""
        name_lists = [ template.names for template in self.templates ]
        return list(itertools.chain.from_iterable(name_lists))

    def get_banish_template(self, invocation: str) -> Optional[BanishTemplate]:
        """Return the appropriate templates based on invocation used."""
        for template in self.templates:
            if template.has_name(invocation):
                return template
        return None

    def get_command_type(self, invocation: str) -> Optional[MuteCommandType]:
        """Return the appropriate MuteCommandType based on invocation used."""
        template = self.get_banish_template(invocation)
        if template:
            return template.get_command_type(invocation)
        return None

    def get_template(self, invocation: str, mute_response: MuteResponseType) -> Optional[Template]:
        """Return the appropriate template."""
        banish_template = self.get_banish_template(invocation)
        if banish_template:
            return banish_template.get_template(mute_response)
        return None
