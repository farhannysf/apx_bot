import sys
import asyncio
import discord
import utility
import logging
import sentry_sdk
import analytics

from discord.ext import commands
from google.cloud import firestore
from sentry_sdk import capture_message

client = commands.Bot(command_prefix='!')

# Initiate Google Cloud Firestore
db = firestore.Client()
keys = utility.retrieveDb_data(db, option='keys', title='api')
 
# Initiate logging and sentry
logging.basicConfig(level=logging.INFO)
sentry_sdk.init(keys['sentryUrl'])

# Initiate Segment analytics
analytics.write_key = keys['segmentKey']

async def serverstatsLogic(ctx, serverTitle):
    try:
        channelList[f'{ctx.message.channel.id}']
    except KeyError:
        return
        
    serverList = utility.retrieveDb_data(db, option='serverlist', title=ctx.message.channel.id)
    
    if serverList is None:
        return await client.say('No server is set. Use `!serverconfig` for more info.')

    try:
        server = serverList[str(serverTitle)]
    
    except KeyError:
        availableServers = '\n'.join('{} (Battlemetrics ID: {})'.format(key, value) for key, value in serverList.items())
        return await client.say(f'`Usage: !serverstats [server name]`\n\nAvailable servers:\n` {availableServers} `')

    serverData = await utility.getData(f'https://api.battlemetrics.com/servers/{server}', params=None, capture_message=capture_message)
        
    if serverData is None:
        return await client.say(f'An error has occured, please contact {author}')
    
    else:
        playerData = await utility.getData('https://api.battlemetrics.com/players', params={'filter[servers]':server, 
            'filter[online]':'true'}, capture_message=capture_message)
        
        if playerData is None:
            return await client.say(f'An error has occured, please contact {author}')

        embed = await utility.embify(serverData, playerData, discord.Embed, capture_message)
        return await client.say(embed=embed)

async def server_updateLogic(ctx, operation, serverTitle, serverId):
    try:
        channelList[f'{ctx.message.channel.id}']
    except KeyError:
        return
        
    serverlistDb = db.collection('serverlist').document(str(ctx.message.channel.id))
    await utility.checkDb(db, serverlistDb, ctx, firestore)
    usageMessage = 'Usage:\n\n`!serverconfig update [server name] [battlmetrics server id]\n!serverconfig delete [server name]`'

    if operation == 'delete':
        if serverTitle is None: 
            return await client.say(usageMessage)
        data = {str(serverTitle): firestore.DELETE_FIELD}
        serverlistDb.update(data)
        return await client.say(f'**Updated server list.**\n `Deleted Server {serverTitle}`')

    if operation == 'update':
        if serverTitle is None or serverId is None:
            return await client.say(usageMessage)
        data = {str(serverTitle):str(serverId)}
        serverlistDb.update(data)
        return await client.say(f'**Updated server list.**\n `Server {serverTitle} (Battlemetrics ID: {serverId})`'), operation, data
    
    else:
        return await client.say(usageMessage)
        
@client.event
async def on_ready():
    print (f'APX Bot Running on {runtime} mode.')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.command(pass_context=True)
async def serverstats(ctx, serverTitle:str=None):
    await serverstatsLogic(ctx, serverTitle)

    analytics.track(ctx.message.author.id, 'Server Info Request', {
        'User ID': ctx.message.author.id,
        'Username': ctx.message.author.name,
        'Channel ID': ctx.message.channel.id,
        'Channel name': ctx.message.channel.name,
        'Guild ID': ctx.message.server.id,
        'Guild name': ctx.message.server.name,
        'server name': serverTitle
    })

@client.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def serverconfig(ctx, operation:str=None, serverTitle:str=None, serverId:int=None):
    await server_updateLogic(ctx, operation, serverTitle, serverId)

    analytics.track(ctx.message.author.id, 'Server List Config Request', {
        'User ID': ctx.message.author.id,
        'Username': ctx.message.author.name,
        'Channel ID': ctx.message.channel.id,
        'Channel name': ctx.message.channel.name,
        'Guild ID': ctx.message.server.id,
        'Guild name': ctx.message.server.name,
        'Operation': operation,
        'server name': serverTitle,
        'Server ID': serverId,
    })
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ('Usage: python3 main.py [runtime]')
        sys.exit()

    author = keys['authorId']
    discordKey = keys['discordToken']
    runtime = sys.argv[1]
    
    if runtime == 'dev':
        discordKey = keys['discordToken_dev']

    channelList = utility.retrieveDb_data(db, option='channellist', title=runtime)
    client.run(discordKey)