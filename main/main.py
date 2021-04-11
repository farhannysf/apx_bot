import sys
import asyncio
import discord
import utility
import logging
import sentry_sdk
import analytics

import gvaw_commands.serverstats
import gvaw_commands.serversearch
import gvaw_commands.serverconfig
import gvaw_commands.channelconfig

from discord.ext import commands
from google.cloud import firestore

client = commands.Bot(command_prefix="!")

# Initiate Google Cloud Firestore
try:
    db = firestore.Client()
except Exception as e:
    credentialError_string = "Could not automatically determine credentials. Please set GOOGLE_APPLICATION_CREDENTIALS or explicitly create credentials and re-run the application. For more information, please see https://cloud.google.com/docs/authentication/getting-started"
    if str(e) == credentialError_string:
        print(
            f"## INVALID CREDENTIALS ##\n\n{credentialError_string}\n\nContact fynugroho@exoduspi.com to be issued the respective Google Cloud Platform credentials to run this software."
        )
    else:
        print(e)
    sys.exit()

keys = utility.retrieveDb_data(db, option="keys", title="api")

# Initiate logging and sentry
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
sentry_sdk.init(keys["sentryUrl"])

# Initiate Segment analytics
analytics.write_key = keys["segmentKey"]


@client.event
async def on_ready():
    logger.info(
        f"Logged in as {client.user.name} ({client.user.id}), running on {runtime} mode.\n------"
    )
    game = discord.Game("!gvawhelp")
    await client.change_presence(status=discord.Status.online, activity=game)


@client.command(pass_context=True)
async def serverstats(ctx, serverTitle: str = None):
    channelId = str(ctx.message.channel.id)
    guildId = str(ctx.message.guild.id)

    await gvaw_commands.serverstats.server_statsLogic(
        ctx, firestore, db, author, channelId, guildId, serverTitle, discord.Embed
    )

    analytics.track(
        ctx.message.author.id,
        "Server Info Request",
        {
            "User ID": ctx.message.author.id,
            "Username": ctx.message.author.name,
            "Channel ID": channelId,
            "Channel name": ctx.message.channel.name,
            "Guild ID": guildId,
            "Guild name": ctx.message.guild.name,
            "Server name": serverTitle,
        },
    )


@serverstats.error
async def serverstats_error(ctx, error):
    logger.error({"cmd": "serverstats", "error": error})
    return await ctx.send(f"An error has occured, please contact {author}")


@client.command(pass_context=True)
async def serversearch(ctx, serverTitle: str = None):
    channelId = str(ctx.message.channel.id)
    guildId = str(ctx.message.guild.id)

    await gvaw_commands.serversearch.server_searchLogic(
        ctx, discord.Embed, firestore, db, author, channelId, guildId, serverTitle
    )

    analytics.track(
        ctx.message.author.id,
        "Server Info Request",
        {
            "User ID": ctx.message.author.id,
            "Username": ctx.message.author.name,
            "Channel ID": channelId,
            "Channel name": ctx.message.channel.name,
            "Guild ID": guildId,
            "Guild name": ctx.message.guild.name,
            "Server name": serverTitle,
        },
    )


@serversearch.error
async def serversearch_error(ctx, error):
    logger.error({"cmd": "serversearch", "error": error})
    return await ctx.send(f"An error has occured, please contact {author}")


@client.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def serverconfig(
    ctx, operation: str = None, serverTitle: str = None, serverId: str = None
):
    channelId = str(ctx.message.channel.id)
    guildId = str(ctx.message.guild.id)

    await gvaw_commands.serverconfig.server_configLogic(
        ctx,
        discord.Embed,
        firestore,
        db,
        channelId,
        guildId,
        operation,
        serverTitle,
        serverId,
    )

    analytics.track(
        ctx.message.author.id,
        "Server List Config Request",
        {
            "User ID": ctx.message.author.id,
            "Username": ctx.message.author.name,
            "Channel ID": channelId,
            "Channel name": ctx.message.channel.name,
            "Guild ID": guildId,
            "Guild name": ctx.message.guild.name,
            "Operation": operation,
            "Server name": serverTitle,
            "Server ID": serverId,
        },
    )


@serverconfig.error
async def serverconfig_error(ctx, error):
    valueError = "Command raised an exception: ValueError"

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "You have no sufficient permission in this guild to use this command. Please contact guild administrator."
        )

    if str(error)[0:39] == valueError:
        await ctx.send("Assigned name must not include any space or special character.")

    else:
        logger.error({"cmd": "serverconfig", "error": error})
        return await ctx.send(f"An error has occured, please contact {author}")


@client.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def channelconfig(ctx, operation: str = None, channel: str = None):
    channelId = str(ctx.message.channel.id)
    guildId = str(ctx.message.guild.id)

    await gvaw_commands.channelconfig.channel_configLogic(
        ctx, discord.Embed, firestore, db, channelId, guildId, operation, channel
    )

    analytics.track(
        ctx.message.author.id,
        "Channel List Config Request",
        {
            "User ID": ctx.message.author.id,
            "Username": ctx.message.author.name,
            "Channel ID": channelId,
            "Channel name": ctx.message.channel.name,
            "Guild ID": guildId,
            "Guild name": ctx.message.guild.name,
            "Operation": operation,
            "Channel set": channel,
        },
    )


@channelconfig.error
async def channelconfig_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "You have no sufficient permission in this guild to use this command. Please contact guild administrator."
        )

    else:
        logger.error({"cmd": "channelconfig", "error": error})
        return await ctx.send(f"An error has occured, please contact {author}")


@client.command(pass_context=True)
async def gvawhelp(ctx):
    channelId = str(ctx.message.channel.id)
    guildId = str(ctx.message.guild.id)

    channelList = utility.retrieveDb_data(db, option="channel-list", title=guildId)
    channelVerify = await utility.checkChannel(
        db, firestore, channelList, channelId, guildId
    )

    if channelVerify:
        gvawHelp = "Display list of commands and usage example.\n------"
        channelConfig = "Authorize or revoke bot access to channels.\n\n`!channelconfig authorize #example-channel`\n\nAuthorize access to #example-channel.\n\n`!channelconfig revoke #example-channel`\n\nRevoke access to #example-channel.\n------"
        serverSearch = "Search for ArmA 3 server IP address by server name.\n\n`!serversearch server name`\n------"
        serverConfig = "Assign or remove ArmA 3/DCS servers to the bot.\n\nYou can specify optional Steam query port for ArmA 3 server on IP address argument.\n\nDCS servers must have -dcs suffix on its name.\n\n`!serverconfig update [name] [IP address]`\n\nAssign a name to ArmA 3 server using the respective IP address and save it to the bot.\n\n`!serverconfig update [name] [IP address:port]`\n\nAssign a name to ArmA 3 server using the respective IP address with optional Steam query port on IP address parameter and save it to the bot.\n\n`!serverconfig update [name-dcs] [IP address]`\n\nAssign a name to DCS server using the respective IP address and save it to the bot.\n\n`!serverconfig delete [name]`\n\nRemove saved server from the bot by the assigned name.\n------"
        serverStats = "Check status of a server by the assigned name.\n\n`!serverstats [name]`\n------"
        authorInfo = f"Contact {author}"

        embed = discord.Embed(
            title="GvAW Help",
            description="List of commands and usage example",
            color=0xE74C3C,
        )

        embed.add_field(name="!gvawhelp", value=gvawHelp, inline=False)
        embed.add_field(name="!serverstats", value=serverStats, inline=False)
        embed.add_field(name="!serversearch", value=serverSearch, inline=False)
        embed.add_field(name="!channelconfig", value=channelConfig, inline=False)
        embed.add_field(name="!serverconfig", value=serverConfig, inline=False)
        embed.add_field(name="More info:", value=authorInfo, inline=False)
        embed.set_thumbnail(url=utility.gvawLogo_url)

        await ctx.send(embed=embed)

        analytics.track(
            ctx.message.author.id,
            "Help Request",
            {
                "User ID": ctx.message.author.id,
                "Username": ctx.message.author.name,
                "Channel ID": channelId,
                "Channel name": ctx.message.channel.name,
                "Guild ID": guildId,
                "Guild name": ctx.message.guild.name,
            },
        )

        return

    return await ctx.send(
        "`This channel is not authorized. Use !channelconfig to authorize channels.`"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py [runtime]")
        sys.exit()

    author = keys["authorId"]
    runtime = sys.argv[1]

    if runtime == "prod":
        discordKey = keys["discordToken"]

    elif runtime == "dev":
        discordKey = keys["discordToken_dev"]

    else:
        print("Usage: python main.py [runtime]")
        sys.exit()

    client.run(discordKey)