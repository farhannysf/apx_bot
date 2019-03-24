import sys
import asyncio
import discord
import utility
import logging
import sentry_sdk
import analytics

import apx_commands.serverstats
import apx_commands.serverconfig
import apx_commands.channelconfig

from discord.ext import commands
from google.cloud import firestore

client = commands.Bot(command_prefix='!')

# Initiate Google Cloud Firestore
db = firestore.Client()
keys = utility.retrieveDb_data(db, option='keys', title='api')
 
# Initiate logging and sentry
logging.basicConfig(level=logging.INFO)
sentry_sdk.init(keys['sentryUrl'])

# Initiate Segment analytics
analytics.write_key = keys['segmentKey']

@client.event
async def on_ready():
    print (f'APX Bot Running on {runtime} mode.')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.command(pass_context=True)
async def serverstats(ctx, serverTitle:str=None):
    channelId = ctx.message.channel.id
    guildId = ctx.message.server.id

    await apx_commands.serverstats.server_statsLogic(client, firestore, db, channelId, guildId, serverTitle, discord.Embed)

    analytics.track(ctx.message.author.id, 'Server Info Request', {
        'User ID': ctx.message.author.id,
        'Username': ctx.message.author.name,
        'Channel ID': channelId,
        'Channel name': ctx.message.channel.name,
        'Guild ID': guildId,
        'Guild name': ctx.message.server.name,
        'Server name': serverTitle
    })

@client.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def serverconfig(ctx, operation:str=None, serverTitle:str=None, serverId:int=None):
    channelId = ctx.message.channel.id
    guildId = ctx.message.server.id

    await apx_commands.serverconfig.server_configLogic(client, firestore, db, channelId, guildId, operation, serverTitle, serverId)

    analytics.track(ctx.message.author.id, 'Server List Config Request', {
        'User ID': ctx.message.author.id,
        'Username': ctx.message.author.name,
        'Channel ID': channelId,
        'Channel name': ctx.message.channel.name,
        'Guild ID': guildId,
        'Guild name': ctx.message.server.name,
        'Operation': operation,
        'Server name': serverTitle,
        'Server ID': serverId,
    })

@client.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def channelconfig(ctx, operation:str=None, channel:str=None):
    channelId = ctx.message.channel.id
    guildId = ctx.message.server.id

    await apx_commands.channelconfig.channel_configLogic(client, firestore, db, channelId, guildId, operation, channel)

    analytics.track(ctx.message.author.id, 'Channel List Config Request', {
        'User ID': ctx.message.author.id,
        'Username': ctx.message.author.name,
        'Channel ID': channelId,
        'Channel name': ctx.message.channel.name,
        'Guild ID': guildId,
        'Guild name': ctx.message.server.name,
        'Operation': operation,
        'Channel set': channel,
    })

@client.command(pass_context=True)
async def apxhelp(ctx):
    channelId = ctx.message.channel.id
    guildId = ctx.message.server.id

    channelList = utility.retrieveDb_data(db, option='channellist', title=guildId)
    channelVerify = await utility.checkChannel(db, firestore, channelList, channelId, guildId)

    if channelVerify:

        helpMessage = ('**__List of Commands__**\n\n• **!apxhelp**\nDisplay help message.\n\n'
            '• **!channelconfig**\nAuthorize or revoke bot access to channels.\n\n'
            '`!channelconfig authorize #example-channel`\nAuthorize bot access to #example-channel.\n\n'
            '`!channelconfig revoke #example-channel`\nRevoke bot access to #example-channel.\n\n• **!serverconfig**\n'
            'Assign or remove ArmA 3 servers on Battlemetrics to the bot.\n\n'
            '`!serverconfig update [name] [battlemetrics id]`\nAssign a name to the respective server using Battlemetrics ID and save it to the bot.\n\n'
            '`!serverconfig delete [name]`\nRemove server from the bot by the assigned name.\n\n• **!serverstats**\nCheck status of saved server.\n\n'
            f'`!serverstats [name]`\nCheck status of a server by the assigned name.\n\nContact {author} for more support.')

        return await client.say(helpMessage)
    
    return await client.say('`This channel is not authorized. Use !channelconfig to authorize channels.`')
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ('Usage: python3 main.py [runtime]')
        sys.exit()

    author = keys['authorId']
    discordKey = keys['discordToken']
    runtime = sys.argv[1]
    
    if runtime == 'dev':
        discordKey = keys['discordToken_dev']

    client.run(discordKey)