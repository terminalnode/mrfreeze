# TODOs
This is a TODO list so I won't forget.
Disclaimer: I tend to forget this document exists.

## Improvements
### Database split
The database is too large, sort of. It holds a lot of different types of information which makes it kind of cool in a way, but also means it's a possible point of failure for a ton of different features. This is what we in the industry call NG or だめだよ - it sucks.

Primary split ideas:
- One for mutes/banishes etc.
- One for quotes.
- One for !region blacklists.

Secondary split ideas (functions not implemented yet):
- One for server settings.
- One for rock, paper, scissors score tables.

### Quotes
Quotes is a travesty and will probably be disabled in the first release of MrFreeze 2.0. Before disabling there are a few changes however that need to be made to the database, though that's mostly included in the database split above.

After MF 2.0 (codename "badass mf") is released, probably, these are the things that need fixing.

Priority 1:
* Make it work with the new DB structure.
* Check that the name isn't all numbers.
* Check for double name entries, all names must be unique.

Priority 2:
* Allow adding last post by a certain user with !quote add @username

Priority 3:
* Merge 'read' and 'random' in cmd_quote.py.
* Some way of saving image attachments.
* Perhaps some kind of emoji-vote function which also adds quotes? React with some obscure(?) emoji, if enough people do it it becomes a quote.

## New features
New features are listed in order of priority.

### Inkcyclopedia
Semi-automatic ink lookup based on klundtasaur's inkcyclopedia:
https://www.reddit.com/r/fountainpens/comments/5egjsa/klundtasaurs_inkcyclopedia_for_rfountainpens/

### !move <ID> #channel
Move one or more posts to a specified channel
* Use post IDs to specify which posts.
* Use a quote-like embed for reposting.

### !disable <ID>
Owner-only command. Disable a certain MrFreeze in one server (enabling multiple concurrent versions to be present).
This is useful because MrFreeze can pull info from multiple servers, enabling *some* support for certain nitro emojis and the like.


## New features (fun times)
Games and other very low priority features/ideas.

### !blackjack
Multiplayer game of blackjack.

### !rps (Rock, paper, scissors)
Rock, paper scissors with a scoreboard.

### !dice
Command for dice throws. Should be able to parse multiple dice and multiple types of dice.
