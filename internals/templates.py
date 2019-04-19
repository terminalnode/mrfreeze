from string import Template
from internals import var

def banish_templates():
    templates = dict()
    all_keys = (
        # Mod mutes:
        'selfmute', 'singlemodmute', 'multimodmute',
        # Freeze mutes:
        'freezemute', 'modfreezemute',
        # User mutes:
        'singlebanish', 'multibanish', 'singlefail', 'multifail', 'mixedfail',
        # Generic
        'past_tense',
    )

    templates['mute'] = {
        # Mod mutes:
        'selfmute'      : Template("I too am tired of hearing your voice $author, but there's not much I can do about it."),
        'singlemodmute' : Template("$author As much as I'd like to I'm afraid I'm not allowed to silence $victim or any other moderator."),
        'multimodmute'  : Template("$author Believe me, if I could I would've shut $victim up a looooong time ago."),

        # Freeze mutes:
        'freezemute'    : Template("$author I will not be silenced!"),
        'modfreezemute' : Template("Hey, $victim! Help! $author is trying to silence us!"),

        # User banishes (TODO):
        'singlebanish' : Template("$author mutes $victim (s.)"),
        'multibanish'  : Template("$author mutes $victim (pl.)"),
        'singlefail'   : Template("$author mutes $victim error $error (s.)"),
        'multifail'    : Template("$author mutes $victim error $error (pl.)"),
        'mixedfail'    : Template("$author mutes $victim but fails to mute $fail error $error"),

        # Generic
        'past_tense'   : "muted",
    }

    templates['banish'] = {
        # Mod banishes:
        'selfmute'      : Template("Oh no $author, you stay away from me! I'm not banishing you here!"),
        'singlemodmute' : Template("$author There's no way I'm sharing a room with $victim!"),
        'multimodmute'  : Template("Oh no, $author is sending the mod gang to attack me! Freeze, smuds!"),

        # Freeze banishes:
        'freezemute'    : Template("$author Are you trying to put me under house arrest?"),
        'modfreezemute' : Template("$author There's no way I'm sharing a room with $victim!"),

        # User banishes (TODO):
        'singlebanish' : Template("$author banishes $victim (s.)"),
        'multibanish'  : Template("$author banishes $victim (pl.)"),
        'singlefail'   : Template("$author banishes $victim error $error (s.)"),
        'multifail'    : Template("$author banishes $victim error $error (pl.)"),
        'mixedfail'    : Template("$author banishes $victim but fails to mute $fail error $error"),

        # Generic
        'past_tense'   : "banished",
    }

    templates['hogtie'] = {
        # Mod banishes (TODO):
        'selfmute'      : Template("$author I'm not hogtie:ing you!! (attempt at self hogtie)"),
        'singlemodmute' : Template("$author I'm not hogtie:ing $victim bcs they're a mod (singular)!"),
        'multimodmute'  : Template("$author I'm not hogtie:ing $victim bcs they're mods (plural)"),

        # Freeze banishes (TODO):
        'freezemute'    : Template("$author is trying to hogtie me, mrfreeze. idk what to say"),
        'modfreezemute' : Template("$author is trying to hogtie me together with $victim (singular or plural)!"),

        # User banishes (TODO):
        'singlebanish' : Template("$author hogties $victim (s.)"),
        'multibanish'  : Template("$author hogties $victim (pl.)"),
        'singlefail'   : Template("$author hogties $victim error $error (s.)"),
        'multifail'    : Template("$author hogties $victim error $error (pl.)"),
        'mixedfail'    : Template("$author hogties $victim but fails to hogtie $fail error $error"),

        # Generic
        'past_tense'   : "hogtied",
    }

    # Test that all keys are present in all themes.
    # Otherwise print an error.
    for theme in templates:
        theme_keys = templates[theme].keys()
        for key in all_keys:
            if key not in theme_keys:
                print(f"{var.cyan}Oi you wanker, {var.red}banish template {theme}{var.cyan}",
                    f"is missing key {var.red}'{key}'{var.cyan}!{var.reset}")

    return templates






















