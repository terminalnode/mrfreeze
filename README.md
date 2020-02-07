# MrFreeze (Rewrite)
This is a rewrite of MrFreeze using cogs instead of mashing everything into a single file. I also hope my adventures in writing MrFreeze will result in a somewhat cleaner bot.

This project uses pipenv. For requirements, see the Pipfile.

It also has a number of "scripts" or commands built-in for running the bot using pipenv:
* **pipenv run bot**         - Starts the bot
* **pipenv run test**        - Runs the tests through pytest (recommended)
* **pipenv run unittest**    - Runs the tests through unittest
* **pipenv run report**      - Runs coverage report to show test coverage
* **pipenv run report_html** - Generates an HTML version of the coverage report in `htmlcov`

By default the pytests will run on all cores at once, using xdist. To disable this behaviour add the option `-n 0`.

## Reimplemented functions:
### Owner commands
* **!restart**   - Restarts the bot. Very useful for testing new code.
* **!gitupdate** - Fetches latest updates from github.

### Mod commands
* **!kick**      - Kicks the user from the server.
* **!purge**     - Purge a certain number of messages. Upper limit is 100 messages.
* **!mute**      - Mutes the user.
* * **!banish**  - Sub-function to mute with a default mute time and custom message.
* **!unmute**    - Unmutes the user.
* **!ban**       - Bans the user from the server.
* **!listban**   - Lists all currently banned users. Can also be called by '!ban list'.
* **!unban**     - Removes ban from the server.

### User utility commands
* **!temp**      - DMs a help message regarding the automatic temperature conversion. Does no conversion of it's own.
* **!rules**     - Displays one, several or all rules depending on how the command is executed.
* **!quote**     - Add, delete, and read random quotes.
* **!vote**      - Creates a vote where users vote by reacting with specified emoji.
* * **Caveat:** This does not work with nitro emojis, but does work with server emojis.
* **!region**    - Allows a user to assign themselves a regional role.
* **!coin**      - Flips a coin. (!coinflip and !cointoss also work)
* **!icon**      - Shows the icon/logo for the current server (!logo also works)

### Silly commands
* **!activity**   - Changes the activity of the bot ('Playing [...]', 'Listening to [...]' etc). No mod requirement, have fun!
* **!mrfreeze**   - Posts a MrFreeze-quote with user instead of Batman and server instead of Gotham.
* Commands which post (more or less) useful links
* * **!readme**    - Posts a link to the github page as well, but to the README.md file (this one!).
* * **!source**    - Posts a link to this github page.
* * **!todo**      - Posts a link to the TODO list for the bot.
* * **!getfreeze** - Posts a link for inviting MrFreeze to your server.
* * **!dummies**   - Posts invite links for the two dummy bots.

### Non-command features
* Will greet a server when coming online.
* Will automatically detect temperature statements and convert them with no user interaction required.
* Will post a message to #mod-discussion when a user leaves.
* Will quote a message that was just pinned so people don't have to check the list of pins. This deletes and replaces the system message.
* * **Caveat:** The bot does a lot of loading when starting up for this to work. If a message was pinned while this loading occurred the next message to get pinned won't be posted, however the next one after that will.
* Will give a rude response when mentioned without a command/temperature statement by someone else.
