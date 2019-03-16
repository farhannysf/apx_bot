import asyncio
import discord
import settings
import logging
import sentry_sdk
import analytics

from discord.ext import commands
from google.cloud import firestore
from sentry_sdk import capture_message

client = commands.Bot(command_prefix='!')

# Initiate Google Cloud Firestore
db = firestore.Client()
keys = settings.retrieveData(db, option='keys', title='api')
 
# Initiate logging and sentry
logging.basicConfig(level=logging.INFO)
sentry_sdk.init(keys['sentryUrl'])

# Initiate Segment analytics
analytics.write_key = keys['segmentKey']

channelList = settings.retrieveData(db, option='channellist', title='channelid')

async def serverstatsLogic(ctx, serverNumber):
    try:
        channelList[f'{ctx.message.channel.id}']
    except KeyError:
        return
        
    serverList = settings.retrieveData(db, option='serverlist', title=ctx.message.channel.id)
    
    if serverList is None:
        return await client.say('No server is set. Use `!serverconfig` for more info.')

    try:
        server = serverList[str(serverNumber)]
    
    except KeyError:
        availableServers = '\n'.join('Server {} (Battlemetrics ID: {})'.format(key, value) for key, value in serverList.items())
        return await client.say(f'`Usage: !serverstats [server number]`\n\nAvailable servers:\n` {availableServers} `')

    serverData = await settings.getData(f'https://api.battlemetrics.com/servers/{server}', params=None, capture_message=capture_message)
        
    if serverData is None:
        return await client.say(f'An error has occured, please contact {author}')
    
    else:
        playerData = await settings.getData('https://api.battlemetrics.com/players', params={'filter[servers]':server, 
            'filter[online]':'true', 'page[size]':serverData['data']['attributes']['maxPlayers']}, capture_message=capture_message)
        embed = await settings.embify(serverData, playerData, discord.Embed, capture_message)
        return await client.say(embed=embed)

async def server_updateLogic(ctx, operation, serverNumber, serverId):
    try:
        channelList[f'{ctx.message.channel.id}']
    except KeyError:
        return
        
    serverlistDb = db.collection('serverlist').document(str(ctx.message.channel.id))
    await settings.checkDb(db, serverlistDb, ctx, firestore)
    usageMessage = 'Usage:\n\n`!serverconfig update [server number] [battlmetrics server id]\n!serverconfig delete [server number]`'

    if operation == 'delete':
        if serverNumber is None: 
            return await client.say(usageMessage)
        data = {str(serverNumber): firestore.DELETE_FIELD}
        serverlistDb.update(data)
        return await client.say(f'**Updated server list.**\n `Deleted Server {serverNumber}`')

    if operation == 'update':
        if serverNumber is None or serverId is None:
            return await client.say(usageMessage)
        data = {str(serverNumber):str(serverId)}
        serverlistDb.update(data)
        return await client.say(f'**Updated server list.**\n `Server {serverNumber} (Battlemetrics ID: {serverId})`'), operation, data
    
    else:
        return await client.say(usageMessage)
        
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.command(pass_context=True)
async def serverstats(ctx, serverNumber:int=None):
    await serverstatsLogic(ctx, serverNumber)

    analytics.track(ctx.message.author.id, 'Server Info Request', {
        'User ID': ctx.message.author.id,
        'Username': ctx.message.author.name,
        'Channel ID': ctx.message.channel.id,
        'Channel name': ctx.message.channel.name,
        'Guild ID': ctx.message.server.id,
        'Guild name': ctx.message.server.name,
        'Server number': serverNumber
    })

@client.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def serverconfig(ctx, operation:str=None, serverNumber:int=None, serverId:int=None):
    await server_updateLogic(ctx, operation, serverNumber, serverId)

    analytics.track(ctx.message.author.id, 'Server List Config Request', {
        'User ID': ctx.message.author.id,
        'Username': ctx.message.author.name,
        'Channel ID': ctx.message.channel.id,
        'Channel name': ctx.message.channel.name,
        'Guild ID': ctx.message.server.id,
        'Guild name': ctx.message.server.name,
        'Operation': operation,
        'Server number': serverNumber,
        'Server ID': serverId,
    })
if __name__ == '__main__':
    author = keys['authorId']
    client.run(keys['discordToken'])

