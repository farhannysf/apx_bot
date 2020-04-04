import sys
import asyncio
import discord
import utility
import logging
import sentry_sdk
import analytics
import webserver

import apx_commands.serverstats
import apx_commands.serversearch
import apx_commands.serverconfig
import apx_commands.channelconfig

from discord.ext import commands
from google.cloud import firestore
from sentry_sdk import capture_message

client = commands.Bot(command_prefix='!')

# Initiate Google Cloud Firestore
try:
    db = firestore.Client()
except Exception as e:
    credentialError_string = 'Could not automatically determine credentials. Please set GOOGLE_APPLICATION_CREDENTIALS or explicitly create credentials and re-run the application. For more information, please see https://cloud.google.com/docs/authentication/getting-started'
    if str(e) == credentialError_string:
        print(f'## INVALID CREDENTIALS ##\n\n{credentialError_string}\n\nContact fynugroho@exoduspi.org to be issued the respective Google Cloud Platform credentials to run this software.')
    else:
        print(e)
    sys.exit()

keys = utility.retrieveDb_data(db, option='keys', title='api')
 
# Initiate logging and sentry
logging.basicConfig(level=logging.INFO)
sentry_sdk.init(keys['sentryUrl'])

# Initiate Segment analytics
analytics.write_key = keys['segmentKey']

@client.event
async def on_ready():
    client.loop.create_task(webserver.sanic_webserver(client, keys, capture_message))
    print (f'APX Bot Running on {runtime} mode.')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    game = discord.Game("!apxhelp")
    await client.change_presence(status=discord.Status.online, activity=game)

@client.command(pass_context=True)
async def serverstats(ctx, serverTitle:str=None):
    channelId = str(ctx.message.channel.id)
    guildId = str(ctx.message.guild.id)

    await apx_commands.serverstats.server_statsLogic(ctx, firestore, db, author, channelId, guildId, serverTitle, discord.Embed, capture_message)

    analytics.track(ctx.message.author.id, 'Server Info Request', {
        'User ID': ctx.message.author.id,
        'Username': ctx.message.author.name,
        'Channel ID': channelId,
        'Channel name': ctx.message.channel.name,
        'Guild ID': guildId,
        'Guild name': ctx.message.guild.name,
        'Server name': serverTitle
    })

@client.command(pass_context=True)
async def serversearch(ctx, serverTitle:str=None):
    channelId = str(ctx.message.channel.id)
    guildId = str(ctx.message.guild.id)

    await apx_commands.serversearch.server_searchLogic(ctx, firestore, db, author, channelId, guildId, serverTitle, capture_message)

    analytics.track(ctx.message.author.id, 'Server Info Request', {
        'User ID': ctx.message.author.id,
        'Username': ctx.message.author.name,
        'Channel ID': channelId,
        'Channel name': ctx.message.channel.name,
        'Guild ID': guildId,
        'Guild name': ctx.message.guild.name,
        'Server name': serverTitle
    })

@client.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def serverconfig(ctx, operation:str=None, serverTitle:str=None, serverId:int=None):
    channelId = str(ctx.message.channel.id)
    guildId = str(ctx.message.guild.id)

    await apx_commands.serverconfig.server_configLogic(ctx, firestore, db, channelId, guildId, operation, serverTitle, serverId)

    analytics.track(ctx.message.author.id, 'Server List Config Request', {
        'User ID': ctx.message.author.id,
        'Username': ctx.message.author.name,
        'Channel ID': channelId,
        'Channel name': ctx.message.channel.name,
        'Guild ID': guildId,
        'Guild name': ctx.message.guild.name,
        'Operation': operation,
        'Server name': serverTitle,
        'Server ID': serverId
    })

@serverconfig.error
async def serverconfig_error(ctx, error):
    valueError = "Command raised an exception: ValueError"
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('You have no sufficient permission in this guild to use this command. Please contact guild administrator.')
    
    if str(error)[0:39] == valueError:
        await ctx.send('Assigned name must not include any space or special character.')
    
    else:
        capture_message(error)



@client.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def channelconfig(ctx, operation:str=None, channel:str=None):
    channelId = str(ctx.message.channel.id)
    guildId = str(ctx.message.guild.id)

    await apx_commands.channelconfig.channel_configLogic(ctx, firestore, db, channelId, guildId, operation, channel)

    analytics.track(ctx.message.author.id, 'Channel List Config Request', {
        'User ID': ctx.message.author.id,
        'Username': ctx.message.author.name,
        'Channel ID': channelId,
        'Channel name': ctx.message.channel.name,
        'Guild ID': guildId,
        'Guild name': ctx.message.guild.name,
        'Operation': operation,
        'Channel set': channel
    })

@channelconfig.error
async def channelconfig_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('You have no sufficient permission in this guild to use this command. Please contact guild administrator.')

    else:
        capture_message(error)


@client.command(pass_context=True)
async def apxhelp(ctx):
    channelId = str(ctx.message.channel.id)
    guildId = str(ctx.message.guild.id)

    channelList = utility.retrieveDb_data(db, option='channellist', title=guildId)
    channelVerify = await utility.checkChannel(db, firestore, channelList, channelId, guildId)

    if channelVerify:

        helpMessage = ('__List of Commands__\n\n• **!apxhelp**\nDisplay help message.\n\n'
            '• **!channelconfig**\nAuthorize or revoke bot access to channels.\n\n'
            '`!channelconfig authorize #example-channel`\nAuthorize bot access to #example-channel.\n\n'
            '`!channelconfig revoke #example-channel`\nRevoke bot access to #example-channel.\n\n• **!serverconfig**\n'
            'Assign or remove ArmA 3 servers on Battlemetrics to the bot.\nAssigned name must not include any space or special character.\n\n'
            '`!serverconfig update [name] [battlemetrics id]`\nAssign a name to the respective server using Battlemetrics ID and save it to the bot.\n\n'
            '`!serverconfig delete [name]`\nRemove saved server from the bot by the assigned name.\n\n• **!serverstats**\nCheck status of saved server.\n\n'
            f'`!serverstats [name]`\nCheck status of a server by the assigned name.\n\n• **!serversearch**\nSearch for ArmA 3 servers Battlemetrics ID.\n\n'
            f'`!serversearch "server name"`\nSearch for Battlemetrics ID by server name.\n\nContact {author} for more support.')

        await ctx.send(helpMessage)
        
        analytics.track(ctx.message.author.id, 'Help Request', {
            'User ID': ctx.message.author.id,
            'Username': ctx.message.author.name,
            'Channel ID': channelId,
            'Channel name': ctx.message.channel.name,
            'Guild ID': guildId,
            'Guild name': ctx.message.guild.name
        })
        
        return

    return await ctx.send('`This channel is not authorized. Use !channelconfig to authorize channels.`')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ('Usage: python main.py [runtime]')
        sys.exit()

    author = keys['authorId']
    runtime = sys.argv[1]

    if runtime == 'prod':
        discordKey = keys['discordToken']
    
    elif runtime == 'dev':
        discordKey = keys['discordToken_dev']
    
    else:
        print ('Usage: python main.py [runtime]')
        sys.exit()

    client.run(discordKey)