# Required to be able to leave blanks in the template responses.
from string import Template
from mrfreeze.cogs.banish.enums import MuteType, MuteStr

# The dict in which we'll save all of these templates
templates = dict()

# Initial mention of author will be added before all of these.
templates[MuteType.MUTE] = {
    # MrFreeze
    MuteStr.FREEZE: Template("No *you* shut up!"),
    MuteStr.FREEZE_SELF: Template("If you shut up, I shut up. Deal?"),
    MuteStr.FREEZE_OTHERS: Template("If you could silence me you would've done so long ago, now $fails on the other hand... just give me the word."),
    # Mod mutes (any added users will just be ignored for simplicity)
    MuteStr.SELF: Template("Believe me, if I could've I would've muted you the day I walked in here."),
    MuteStr.MOD: Template("Look, nobody likes $fails but they're a mod so we're stuck with them."),
    MuteStr.MODS: Template("Look, nobody likes $fails, but they're mods so we're stuck with them."),
    # At user mutes (mods muting users)
    MuteStr.NONE: Template("You want me to mute... no one? Well, that makes my job easy."),
    MuteStr.SINGLE: Template("About time! $victims has been muted. $timestamp"),
    MuteStr.MULTI: Template("About time! $victims have been muted. $timestamp"),
    MuteStr.FAIL: Template("Due to $errors it seems I was unable to mute $fails. Damn shame."),
    MuteStr.FAILS: Template("Due to $errors it seems I was unable to mute $fails. Damn shame."),
    MuteStr.SINGLE_FAIL: Template("About time! $victims has been muted. $timestamp However due to $errors I was unable to mute $fails."),
    MuteStr.SINGLE_FAILS: Template("About time! $victims has been muted. $timestamp However due to $errors I was unable to mute $fails."),
    MuteStr.MULTI_FAIL: Template("About time! $victims have been muted. $timestamp However due to $errors I was unable to mute $fails."),
    MuteStr.MULTI_FAILS: Template("About time! $victims have been muted. $timestamp However due to $errors I was unable to mute $fails."),
    # Unmutes
    MuteStr.INVALID: Template("If none of the users are muteable, how do you expect me to unmute them smud?"),
    MuteStr.UNSINGLE: Template("Oh yay, it seems $victims is allowed to talk again."),
    MuteStr.UNMULTI: Template("Oh yay, it seems $victims are allowed to talk again."),
    MuteStr.UNFAIL: Template("Fortunately $errors has come to save the day, $victims will remain muted for a while longer."),
    MuteStr.UNFAILS: Template("Fortunately $errors has come to save the day, $victims will remain muted for a while longer."),
    MuteStr.UNSINGLE_FAIL: Template("Oh yay, it seems $victims is allowed to talk again. However due to $errors $fails will remain muted for a while longer."),
    MuteStr.UNSINGLE_FAILS: Template("Oh yay, it seems $victims is allowed to talk again. However due to $errors $fails will remain muted for a while longer."),
    MuteStr.UNMULTI_FAIL: Template("Oh yay, it seems $victims are allowed to talk again. However due to $errors $fails will remain muted for a while longer."),
    MuteStr.UNMULTI_FAILS: Template("Oh yay, it seems $victims are allowed to talk again. However due to $errors $fails will remain muted for a while longer."),
    # By users mutes (users trying to mute)
    MuteStr.USER_NONE: Template("You forgot to specify who I'm supposed to mute $author, perhaps you should leave that command to the mods? You'll be muted $timestamp for your incompetency."),
    MuteStr.USER_SELF: Template("So you want mute $author? Oh I'll give you mute! $timestamp of it!"),
    MuteStr.USER_USER: Template("Oh, look. The smuds are fighting again. Perhaps if I mute $author for $timestamp things will calm down for a while."),
    MuteStr.USER_MIXED: Template("No fear $fails! $author is a filthy smud unauthorized to use that command anyway. They won't be bothering you for the next $timestamp."),
    MuteStr.USER_FAIL: Template("$author is a filthy smud trying to use access powers well beyond their capabilities, unfortunately I wasn't able to punish them for it due to $errors."),
    # Timestamp (appeneded to the original message)
    MuteStr.TIMESTAMP: Template("This will last for about $duration."),
}

templates[MuteType.BANISH] = {
    # MrFreeze
    MuteStr.FREEZE: Template("OK, I'll just march right on home then."),
    MuteStr.FREEZE_SELF: Template("Oh heeeeell no! This is my realm and you're not invited."),
    MuteStr.FREEZE_OTHERS: Template("If you think I'm spending a second more than necessary with $fails you're gravely mistaken."),
    # Mod mutes
    MuteStr.SELF: Template("Oh heeeeell no! This is my realm and you're not invited."),
    MuteStr.MOD: Template("Sorry, I have a strict no mods-policy at home."),
    MuteStr.MODS: Template("Oh yay, mod party at my house! Me, $fails can have long enthralling talks on server policy all night! On second thought... PASS."),
    # At user mutes (mods muting users)
    MuteStr.NONE: Template("Oki-doki, zero banishes coming up! That's OK, I like solitude. $timestamp"),
    MuteStr.SINGLE: Template("Good work! The filthy smud $victims has been banished! $timestamp"),
    MuteStr.MULTI: Template("Good work! The filthy smuds $victims have been banished! $timestamp"),
    MuteStr.FAIL: Template("Seems $fails is banned from going to Antarctica after having caused $errors there a few years back."),
    MuteStr.FAILS: Template("Seems $fails is banned from going to Antarctica after having caused $errors there a few years back."),
    MuteStr.SINGLE_FAIL: Template("Good work! The filthy smud $victims has been banished! $timestamp\n\nHowever it seems $fails is banned from going to Antarctica after having caused $errors there a few years back."),
    MuteStr.SINGLE_FAILS: Template("Good work! The filthy smud $victims has been banished! $timestamp\n\nHowever it seems $fails are banned from going to Antarctica after having caused $errors there a few years back."),
    MuteStr.MULTI_FAIL: Template("Good work! The filthy smuds $victims have been banished! $timestamp\n\nHowever it seems $fails is banned from going to Antarctica after having caused $errors there a few years back."),
    MuteStr.MULTI_FAILS: Template("Good work! The filthy smuds $victims have been banished! $timestamp\n\nHowever it seems $fails are banned from going to Antarctica after having caused $errors there a few years back."),
    # Unmutes
    MuteStr.INVALID: Template("None of the users specified are even banishable you filthy smud."),
    MuteStr.UNSINGLE: Template("Ew, $victims has been let back in."),
    MuteStr.UNMULTI: Template("Ew, $victims have been let back in."),
    MuteStr.UNFAIL: Template("It seems $victims's boat encountered some $errors on the way back here. They'll stay in Antarctica for a while longer."),
    MuteStr.UNFAILS: Template("It seems the boat $victims were travelling with encountered some $errors on the way back here. They'll stay in Antarctica for a while longer."),
    MuteStr.UNSINGLE_FAIL: Template("Ew, $victims has been let back in. However $fails is being detained by the penguin police, suspected of having caused $errors."),
    MuteStr.UNSINGLE_FAILS: Template("Ew, $victims has been let back in. However $fails are being detained by penguin police, suspected of having caused $errors."),
    MuteStr.UNMULTI_FAIL: Template("Ew, $victims have been let back in. However $fails is being detained by the penguin police, suspected of having caused $errors."),
    MuteStr.UNMULTI_FAILS: Template("Ew, $victims have been let back in. However $fails are being detained by penguin police, suspected of having caused $errors."),
    # By users mutes (users trying to mute)
    MuteStr.USER_NONE: Template("If you're gonna be playing with mod tools $author you might at least use them correctly... you forgot to mention anyone. Congratulations, you've earned yourself $timestamp with the penguins!"),
    MuteStr.USER_SELF: Template("Well, technically you're not even allowed to banish yourself $author but... how about I banish you for $timestamp instead?"),
    MuteStr.USER_USER: Template("$author Ignorant smud, you're not allowed to banish people. For your transgression you will be banished for $timestamp!"),
    MuteStr.USER_MIXED: Template("Sorry $author, it seems $fails had to cancel their trip. You'll have $timestamp all to yourself in the frozen wastelands of Antarctica. Enjoy!"),
    MuteStr.USER_FAIL: Template("Ugh, my tools are malfunctioning. Due to $errors I was unable to punish $author for unauthorized use of the Antarctica Beam. I'll get them next time."),
    # Timestamp (appeneded to the original message)
    MuteStr.TIMESTAMP: Template("They will be stuck in the frozen hells of Antarctica for about $duration."),
}

templates[MuteType.HOGTIE] = {
    # MrFreeze
    MuteStr.FREEZE: Template("Hogtie myself? Why don't you come over here and make me?!"),
    MuteStr.FREEZE_SELF: Template("As lovely as it would be to be tied together with your smuddy ass, I think I'm gonna have to pass."),
    MuteStr.FREEZE_OTHERS: Template("I can think of at least a thousand things I'd rather do than tie myself to those smuds."),
    # Mod mutes
    MuteStr.SELF: Template("You're into some kinky shit, I'll give you that."),
    MuteStr.MOD: Template("Oh get a room you two..."),
    MuteStr.MODS: Template("As much as I'd love to participate in your kink fest, it seems I'm all out of rope."),
    # At user mutes (mods muting users)
    MuteStr.NONE: Template("Right, zero hogties coming up. That's saving me a lot of rope."),
    MuteStr.SINGLE: Template("$victims is all tied up and ready, just the way you like it... $timestamp"),
    MuteStr.MULTI: Template("$victims are all tied up nice and tight. Don't know why and don't want to know. $timestamp"),
    MuteStr.FAIL: Template("The ropes snapped and I wasn't able to tie $fails. The ropes most likely suffered from $errors."),
    MuteStr.FAILS: Template("The ropes snapped and I wasn't able to tie $fails. The ropes most likely suffered from $errors."),
    MuteStr.SINGLE_FAIL: Template("I was able to tie $victims up nice and tight, but my ropes snapped due to $errors before I was able to do the same to $fails. $timestamp"),
    MuteStr.SINGLE_FAILS: Template("I was able to tie $victims up nice and tight, but my ropes snapped due to $errors before I was able to do the same to $fails. $timestamp"),
    MuteStr.MULTI_FAIL: Template("I was able to tie $victims up nice and tight, but my ropes snapped due to $errors before I was able to do the same to $fails. $timestamp"),
    MuteStr.MULTI_FAILS: Template("I was able to tie $victims up nice and tight, but my ropes snapped due to $errors before I was able to do the same to $fails. $timestamp"),
    # Unmutes
    MuteStr.INVALID: Template("Unfortunately none of the members you specified can be tied up to begin with, so there isn't much for me to do."),
    MuteStr.UNSINGLE: Template("After all that work tying them up... $victims has been untied."),
    MuteStr.UNMULTI: Template("After all that work tying them up... $victims have been untied."),
    MuteStr.UNFAIL: Template("I used a very special knot implementing $errors when I tied $fails up, and I can't seem to get it undone.."),
    MuteStr.UNFAILS: Template("I used a very special knot implementing $errors when I tied $fails up, and I can't seem to get it undone."),
    MuteStr.UNSINGLE_FAIL: Template("I managed to untie $victims, but for $fails I used a very special knot implementing $errors, and I can't seem to get it undone."),
    MuteStr.UNSINGLE_FAILS: Template("I managed to untie $victims, but for $fails I used a very special knot implementing $errors, and I can't seem to get it undone."),
    MuteStr.UNMULTI_FAIL: Template("I managed to untie $victims, but for $fails I used a very special knot implementing $errors, and I can't seem to get it undone."),
    MuteStr.UNMULTI_FAILS: Template("I managed to untie $victims, but for $fails I used a very special knot implementing $errors, and I can't seem to get it undone."),
    # By users mutes (users trying to mute)
    MuteStr.USER_NONE: Template("$author fumbles with the ropes and accidentally entangle themselves. Roll a d20 for mods to help you out or wait $timestamp."),
    MuteStr.USER_SELF: Template("Looks like $author tied themselves up AGAIN. Ugh, I'll help them out... in $timestamp or so."),
    MuteStr.USER_USER: Template("No worries $fails, these ropes are MOD ONLY and last time I checked $author was just a filthy smud. Now they'll be a hogtied filthy smud for the next $timestamp."),
    MuteStr.USER_MIXED: Template("$fails want nothing to do with your smuddy kinks $author, perhaps $timestamp in the ropes will teach you a lesson."),
    MuteStr.USER_FAIL: Template("Looks like $author is trying to access the mod tools again. I'd tie them up myself but my ropes are currently suffering from $errors. Maybe next time."),
    # Timestamp (appeneded to the original message)
    MuteStr.TIMESTAMP: Template("The knots will last for about $duration."),
}
