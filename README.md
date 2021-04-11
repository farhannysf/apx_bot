# [GVAW] Bot
A simple Discord bot to check for ArmA 3 and DCS server status.

# About
This project is made to improve players convenience and reduce time spent when checking current mission and number of players of ArmA 3 and DCS servers through Discord integration.

# Features
The bot is able to show current mission, number of players and active players list on a server when [!serverstats](#serverstats) command is invoked by a user. 

It asynchronously fetches ArmA 3 server data directly from the host server's Steam query port (which defaults to port 2303 if not specified by user) with [python-a2s](#tools) while DCS server data is asynchronously fetched through [DCS official website](https://www.digitalcombatsimulator.com/) server list. 

Users can browse through the list of ArmA 3 servers on [Battlemetrics](#api) by server name to retrieve the server IP with [!serversearch](#serversearch) command. 

Channel authorization can be managed by users with sufficient permission in the Discord guild through [!channelconfig](#channelconfig) command. 

Respectively, server list can also be managed by by users with sufficient permission in the Discord guild through [!serverconfig](#serverconfig) command. 

The bot is also containerized using Docker with image pulled from [Platform One](https://p1.dso.mil/) registry to provide more security and portability in deployment. 

It is using Sentry for logging and error tracking, Segment with Amplitude integration for analytics and Google Cloud Firestore to store channel, server list and configuration variables. 

There are two available built-in runtime modes, each accomodates for development and production purpose. This is designed to keep environments across the application lifecycle as similar as possible and maximize dev/prod parity.

# Usage
### !gvawhelp
Display help message.

![help](https://raw.githubusercontent.com/farhannysf/apx_bot/gvaw/docs/help.png)

---

### !channelconfig
Authorize or revoke bot access to channels.

###### `!channelconfig authorize #example-channel`
Authorize bot access to #example-channel.

###### `!channelconfig revoke #example-channel`
Revoke bot access to #example-channel.

![channelconfig](https://raw.githubusercontent.com/farhannysf/apx_bot/gvaw/docs/channelconfig.png)

---

### !serversearch
Search for ArmA 3 servers IP address.

###### `!serversearch server name`
Search for ArmA 3 server IP address by server name.

![serversearch](https://raw.githubusercontent.com/farhannysf/apx_bot/gvaw/docs/serversearch.png)

---

### !serverconfig
Assign or remove ArmA 3/DCS servers to the bot.

You can specify optional Steam query port for ArmA 3 server on IP address argument.

DCS servers must have -dcs suffix on its name.

###### `!serverconfig update [name] [IP address]`
Assign a name to ArmA 3 server using the respective IP address and save it to the bot.

###### `!serverconfig update [name] [IP address:port]`
Assign a name to ArmA 3 server using the respective IP address with optional Steam query port on IP address parameter and save it to the bot.

###### `!serverconfig update [name-dcs] [IP address]`
Assign a name to DCS server using the respective IP address and save it to the bot.

###### `!serverconfig delete [name]`
Remove saved server from the bot by the assigned name.

![serverconfig](https://raw.githubusercontent.com/farhannysf/apx_bot/gvaw/docs/serverconfig.png)

---

### !serverstats
Check status of saved server.

###### `!serverstats [name]`
Check status of a server by the assigned name.

![serverstats](https://raw.githubusercontent.com/farhannysf/apx_bot/gvaw/docs/serverstats.png)

---

# Sites/Tools used

### Tools
* [aiohttp](https://docs.aiohttp.org/en/stable/)
* [asyncio](https://docs.python.org/3.6/library/asyncio.html)
* [discord.py](https://discordpy.readthedocs.io/en/latest/)
* [python-a2s](https://github.com/Yepoleb/python-a2s)
* [sentry-sdk](https://docs.sentry.io/error-reporting/quickstart/?platform=python)
* [analytics-python](https://segment.com/docs/sources/server/python/)
* [google-cloud-firestore](https://cloud.google.com/firestore/docs/quickstart-servers)

### API
* [Battlemetrics](https://www.battlemetrics.com/developers/documentation)

### Sites
* [Segment](https://segment.com/)
* [Amplitude](https://amplitude.com/)
* [Google Cloud Platform](https://cloud.google.com/)