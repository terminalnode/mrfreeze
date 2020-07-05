# MrFreeze 2.1+
This is the post-release plans for MrFreeze that will likely not make it in for version 2.0 (but might)

### Inkcyclopedia
Status: done, needs to be ported to new database thing

Semi-automatic ink lookup based on klundtasaur's inkcyclopedia:
https://www.reddit.com/r/fountainpens/comments/5egjsa/klundtasaurs\_inkcyclopedia\_for\_rfountainpens/

## Remake the !region command
Status: work not started

The current region command sucks and should use some kind of database solution instead, where moderators
can edit

### Tests
**Region**
* ...blacklisted users can't and non-blacklisted users can change regions.
* ...mods can and non-mods can't edit the blacklist.
* ...listing of regions work.
* ...mods can and non-mods can't produce a list of blacklisted people.

## !quotes
Status: somewhat completed, but going to need a lot of reworking.

* Make a new database for it it.
* Check that the name isn't all numbers.
* Check for double name entries, all names must be unique.
* Allow adding last post by a certain user with !quote add @username
* Merge 'read' and 'random' in cmd_quote.py.
* Some way of saving image attachments.
* Perhaps some kind of emoji-vote function which also adds quotes? React with some obscure(?) emoji, if enough people do it it becomes a quote.

## !blackjack
Status: work not started

Multiplayer game of blackjack.

## !rps (Rock, paper, scissors)
Status: work not started

Rock, paper scissors with a scoreboard.

## !dice
Status: work not started

Command for dice throws. Should be able to parse multiple dice and multiple types of dice.
