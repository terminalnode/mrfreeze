# MrFreeze (Rewrite)
This is a rewrite of MrFreeze using cogs instead of mashing everything into a single file. I also hope my adventures in writing MrFreeze will result in a somewhat cleaner bot.

**Requirements:** python 2.6.6, discord.py (rewrite), inflect

## Reimplemented functions:
### Owner commands
* **!restart**   - Restarts the bot. Very useful for testing new code.
* **!gitupdate** - Fetches latest updates from github.

### Mod commands
* TBA

### User utility commands
* **!temp**     - DMs a help message regarding the automatic temperature conversion. Does no conversion of it's own.
* **!rules**    - Displays one, several or all rules depending on how the command is executed.
* **!quote**     - Add, delete, and read random quotes.

### Silly commands
* **!mrfreeze**  - Posts a MrFreeze-quote with user instead of Batman and server instead of Gotham.
* **!source**    - Posts a link to this github page.
* **!dummies**   - Invite links for the dummy bots Ba'athman and Robin.
* **!readme**    - Posts a link to the github page as well, but to the README.md file (this one!).

### Non-command features
* Will greet a server when coming online.
* Will automatically detect temperature statements and convert them with no user interraction required.
* Will post a message to #mod-discussion when a user leaves.
* Will quote a message that was just pinned so people don't have to check the list of pins.
* * Caveat: The bot does a lot of loading when starting up for this to work. If a message was pinned while this loading occured the next message to get pinned won't be posted, however the next one after that will.

## Todo
### Commands
* **!unban**     - (Mod) Removes ban from the server.
* **!banish**    - (Mod) Assigns the role 'Antarctica' to a user for five minutes.
* **!ban**       - (Mod) Bans the user from the server.
* **!kick**      - (Mod) Kicks the user from the server.
* **!mute**      - (Mod) Mutes the user.
* **!unmute**    - (Mod) Unmutes the user.
* **!activity**  - Changes the activity of the bot ('Playing [...]'). No mod requirement, have fun!
* **!region**    - Allows a user to assign a regional role such as continent (could also be used for countries).
* **!vote**      - Creates a vote where users vote by reacting with specified emoji.
* * This does not work with nitro emojis, but does work with server emojis.
* **!rps**       - Play rock, paper, scissors with the bot. With scores!
* **!dice**      - Roll a select number of dice. Intend to also implement option to select type of dice.

### Far-Away ideas/commands
* **!ink**       - Attempt to bring the ink look-up used on r/fountainpens to discord.
* **!blackjack** - A game of blackjack.
