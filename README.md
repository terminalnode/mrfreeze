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
* **!vote**      - Creates a vote where users vote by reacting with specified emoji.
* * **Caveat:** This does not work with nitro emojis, but does work with server emojis.
* **!region**    - Allows a user to assign themselves a regional role.

### Silly commands
* **!activity**  - Changes the activity of the bot ('Playing [...]', 'Listening to [...]' etc). No mod requirement, have fun!
* **!dummies**   - Invite links for the dummy bots Ba'athman and Robin.
* **!mrfreeze**  - Posts a MrFreeze-quote with user instead of Batman and server instead of Gotham.
* **!readme**    - Posts a link to the github page as well, but to the README.md file (this one!).
* **!source**    - Posts a link to this github page.

### Non-command features
* Will greet a server when coming online.
* Will automatically detect temperature statements and convert them with no user interaction required.
* Will post a message to #mod-discussion when a user leaves.
* Will quote a message that was just pinned so people don't have to check the list of pins. This deletes and replaces the system message.
* * **Caveat:** The bot does a lot of loading when starting up for this to work. If a message was pinned while this loading occurred the next message to get pinned won't be posted, however the next one after that will.
* Will give a rude response when mentioned without a command/temperature statement by someone else.

## Todo
### Commands
* **!unban**     - (Mod) Removes ban from the server.
* **!ban**       - (Mod) Bans the user from the server.
* **!kick**      - (Mod) Kicks the user from the server.
* **!mute**      - (Mod) Mutes the user.
* * **!banish**  - Sub-function to mute with a default mute time and custom message.
* **!unmute**    - (Mod) Unmutes the user.
* **!purge**     - (Mod) Purge a certain number of messages.
* **!rps**       - Play rock, paper, scissors with the bot. With scores!
* **!dice**      - Roll a select number of dice. Intend to also implement option to select type of dice.
* **!help**      - We're going to have a reimplemented version of !help.

### Far-Away ideas/commands
* **!ink**       - Attempt to bring the ink look-up used on r/fountainpens to discord.
* **!blackjack** - A game of blackjack.
