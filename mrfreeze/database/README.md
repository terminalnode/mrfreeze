# Settings module
This is the settings module for MrFreeze. It's organised so that the bot will only ever
need a single instance of the Settings class, which will then have instances of the
various sub modules. The sub modules in turn have one module for each table they administrate.

For example, the `server_settings` module keeps track of which channels are designated as
mute channels (in The Penposium server, this would be the #antarctica channel) to which banish
messages and the likes are posted. Creation of this mute channels table is handled by the
`mute_channels` module that is instantiated by `ServerSettings`. All methods in `MuteChannels`
are linked through `ServerSettings` to `Settings` and thus made available to the bot.
