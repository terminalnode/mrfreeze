"""Module for reading the string template responses for banish."""

import itertools
from enum import Enum
from string import Template
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import MutableMapping

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


class BanishTemplate:
    """Class for holding a single template."""

    data: MutableMapping[str, Any]
    filename: str
    names: List[str]
    templates: Dict[MuteResponse, Template]

    def __init__(self, file: str) -> None:
        print(f"Hello, {file} here!")
        self.data = toml.load(f"config/banish_templates/{file}")
        self.filename = file
        self.names = list()
        self.templates = dict()

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

        main_name = self.strip_iterable(names.get("main"))
        undo_name = self.strip_iterable(names.get("undo"))
        micro_name = self.strip_iterable(names.get("micro"))
        super_name = self.strip_iterable(names.get("super"))
        mega_name = self.strip_iterable(names.get("mega"))

        if not main_name:
            raise MissingNameException(f"{self.filename} is missing names => main")
        elif not undo_name:
            raise MissingNameException(f"{self.filename} is missing names => undo")

        unflattened_aliases = [ main_name, undo_name ]
        unflattened_aliases += [ name for name in [ micro_name, super_name, mega_name ] if name ]
        self.names = list(itertools.chain.from_iterable(unflattened_aliases))

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
        if not templates:
            error = f"{self.filename} is missing templates section."
            raise MissingTemplateException(error)

        for template in MuteResponse:
            template_string = templates.get(template.value)
            if not template_string:
                error = f"{self.filename} is missing template: {template.value}"
                raise MissingTemplateException(error)

            self.templates[template] = Template(template_string)

    def strip_iterable(self, iterable: Iterable) -> Iterable:
        """Remove all empty strings from an iterable."""
        if iterable:
            return [ i for i in iterable if isinstance(i, str) and i ]
        else:
            return iterable


class TemplateEngine:
    """Class for holding all templates."""

    templates: List[BanishTemplate]

    def __init__(self, files: Iterable[str] = files) -> None:
        self.templates = list()

        for file in files:
            print(file)
            new_template = BanishTemplate(file)
            new_template.parse_names(self.templates)
            self.templates.append(new_template)

        print(f"Loaded {len(self.templates)}!")

    def get_aliases(self) -> List[str]:
        """Get a list of all command names."""
        name_lists = [ template.names for template in self.templates ]
        return list(itertools.chain.from_iterable(name_lists))
