# MrFreeze
MrFreeze is the chat bot designed for [The Penposium](https://discord.gg/FRSg6f5)
Discord server, which is probably the largest chat dedicated to fountain pens there
is. If you're interested in fountain pens you should check it out, they're a friendly
bunch. :)

## Feature suggestions and bug reports
Feel free to suggest new features and/or report bugs you've discovered via
the repository's [issues section](https://github.com/terminalnode/mrfreeze/issues).

## Contributing
Anyone in The Penposium discord server with some knowledge of Python is welcome to
contribute. Contact me (TerminalNode#1917 on Discord) via DM or in the dev server
[MrFreeze's Cave](https://discord.com/invite/wcwshah) and I'll help you get up to
speed and coordinate our efforts.

For suggestions on what to do, check out the current
[list of issues](https://github.com/terminalnode/mrfreeze/issues).

Also take a look at the next section on how to get the bot up and running.

## Running the bot
This project uses [pipenv](https://github.com/pypa/pipenv/), a tool for managing
dependencies and automatically setup virtual environments. Just run `pipenv install --dev`
and it should supply you with anything you need.
If you have [pyenv](https://github.com/pyenv/pyenv) installed it will even install
the correct version of python if you don't have it already.

In addition to this you will have to create a plain text file called `token` in the
project root directory. This text file should contain a single line with your bots
token (which you can get through the discord developer portal).

To run the bot or the tests in the pipenv environtment, use one of the following commands:
* **pipenv run bot**         - Starts the bot
* **pipenv run test**        - Runs the tests through pytest (recommended)
* **pipenv run unittest**    - Runs the tests through unittest
* **pipenv run report**      - Runs coverage report to show test coverage
* **pipenv run report_html** - Generates an HTML version of the coverage report in `htmlcov`

By default the pytests will run on all cores at once, using xdist.
To disable this behaviour add the option `-n 0`.

## Why is there one folder called `database` and one called `databases`?
Valid question. The bot stores some data, perhaps most notably the list of muted
users, in SQLite databases. The key word here being database**s** plural.

In the beginning of the project every table had it's own database, the idea being that
if one wanted to reset a given table one could simply delete that file and there'd
be no reason to worry about affecting the other tables.

This approach is a bit silly however, and results in a lot of duplicate code for
all of the tables. As such there's been some effort to create some sort of unified
framework for database tables, and saving all of these tables in a single database.

Modules using the old system are stored in `databases`, modules using the new system
are stored in `database`.

The new system is as of yet incomplete and can only hold one kind of table, which is
a table where each server has exactly one row and one value. There is some work being
done to also create a base where one server can have multiple rows with one value each.
As of yet, nothing has been implemented to hold more complex tables with an arbitrary
number of columns - such as is required for the mutes database.
