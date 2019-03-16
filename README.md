# [APX] Bot
A simple Discord bot to show APX servers status for ArmA 3.

# About
This project is made to improve players convenience and reduce time spent when checking current mission and number of players of APX ArmA 3 servers through Discord integration.

# Features
The bot is actively hosted on APX Discord guild. It is able to show current mission, number of players and active players list on a server when !serverstats command is invoked by a user. Server list can be managed by authorized users through !serverconfig commands. The bot is also containerized using Docker to provide more portability in deployment. It is using Sentry for logging and error tracking, Segment with Amplitude integration for analytics and Google Cloud Firestore to store server list and configuration variables.

### Usage example

![Alt Text](https://github.com/farhannysf/apx_bot/blob/master/docs/apxbot.gif)

# Sites/Tools used

### Tools
* [aiohttp](https://docs.aiohttp.org/en/stable/)
* [asyncio](https://docs.python.org/3.6/library/asyncio.html)
* [discord.py](https://discordpy.readthedocs.io/en/latest/)
* [python-dotenv](https://github.com/theskumar/python-dotenv)
* [sentry-sdk](https://docs.sentry.io/error-reporting/quickstart/?platform=python)
* [analytics-python](https://segment.com/docs/sources/server/python/)
* [google-cloud-firestore](https://cloud.google.com/firestore/docs/quickstart-servers)

### API
* [Battlemetrics](https://www.battlemetrics.com/developers/documentation)

### Site
* [Segment](https://segment.com/)
* [Amplitude](https://amplitude.com/)
