import sys
import re
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

async def server_statsLogic(channelId, guildId, serverTitle):
    channelList = utility.retrieveDb_data(db, option='channellist', title=guildId)
    channelVerify = await utility.checkChannel(db, firestore, channelList, channelId, guildId)
    
    if channelVerify:
        
        serverList = utility.retrieveDb_data(db, option='serverlist', title=guildId)
        
        if serverList is None:
            return await client.say('No server is set. Use `!serverconfig` for more info.')

        try:
            server = serverList[str(serverTitle)]
        
        except KeyError:
            availableServers = '\n'.join('{} (Battlemetrics ID: {})'.format(key, value) for key, value in serverList.items())
            return await client.say(f'**Usage:**\n\n`!serverstats [server name]`\n\n**Available Servers:**\n\n` {availableServers} `')

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
    
    else:
        return await client.say('`This channel is not authorized. Use !channelconfig to authorize channels.`')

async def server_configLogic(channelId, guildId, operation, serverTitle, serverId):
    channelList = utility.retrieveDb_data(db, option='channellist', title=guildId)
    channelVerify = await utility.checkChannel(db, firestore, channelList, channelId, guildId)

    if channelVerify:
        serverList = utility.retrieveDb_data(db, option='serverlist', title=guildId)
        serverlistDb = db.collection('serverlist').document(str(guildId))
        await utility.checkDb(db, serverList, serverlistDb,firestore)
        usageMessage = '**Usage:**\n\n`!serverconfig update [server name] [battlmetrics server id]\n!serverconfig delete [server name]`'

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
            return await client.say(f'**Updated server list.**\n `Server {serverTitle} (Battlemetrics ID: {serverId})`')
        
        else:
            return await client.say(usageMessage)
    else:
        return await client.say('`This channel is not authorized. Use !channelconfig to authorize channels.`')

async def channel_configLogic(channelId, guildId, operation, channel):
    channelList = utility.retrieveDb_data(db, option='channellist', title=guildId)
    await utility.checkChannel(db, firestore, channelList, channelId, guildId)
    availableChannels = '\n'.join('<#{}>'.format(key) for key, value in utility.retrieveDb_data(db, option='channellist', title=guildId).items())

    usageMessage = f'**Usage:**\n\n`!channelconfig authorize [#channel]`\n`!channelconfig revoke [#channel]`\n\n**Authorized Channels:**\n\n{availableChannels}'
    if operation:
        if channel:
            channellist_Db = db.collection('channellist').document(str(guildId))
            try:
                channelSelect = int(re.search(r'\d+', channel).group())
            except:
                return await client.say('Please input the correct channel format, e.g. `#example`.')
            if operation == 'authorize':
                data = {str(channelSelect):str(channelSelect)}
                channellist_Db.update(data)
                return await client.say(f'**Updated authorized channel list.**\n <#{channelSelect}> `is now authorized`')
                
            if operation == 'revoke':
                data = {str(channelSelect): firestore.DELETE_FIELD}
                channellist_Db.update(data)
                return await client.say(f'**Updated authorized channel list.**\n `Revoked access from` <#{channelSelect}>')
    
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
    channelId = ctx.message.channel.id
    guildId = ctx.message.server.id

    await server_statsLogic(channelId, guildId, serverTitle)

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

    await server_configLogic(channelId, guildId, operation, serverTitle, serverId)

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

    await channel_configLogic(channelId, guildId, operation, channel)

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