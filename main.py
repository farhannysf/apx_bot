import asyncio
import aiohttp
import discord
import settings
import discord
import logging
import sentry_sdk

from discord.ext import commands
from sentry_sdk import capture_message

logging.basicConfig(level=logging.INFO)
sentry_sdk.init("https://d848feec91f2467580211ae19b5538a2@sentry.io/1371559")
client = commands.Bot(command_prefix='!')

serverList = {1:'1015436', 4:'3244423'}

async def asyncGet(*args, **kwargs):
    async with aiohttp.ClientSession() as client:
        async with client.get(*args, **kwargs) as response:
            response.body = await response.read()

            return response

async def getData(url, params):
    response = await asyncGet(url, params=params)
    
    if response.status == 203:
        data = await response.json()
        return data    
    else:
        capture_message(f'Battlemetrics API: {response.status}')
    
async def embify(serverData, playerData):
    if not playerData['data']:
        players = 'No active players.'
    
    else:
        playerList = [item['attributes']['name'] for item in playerData['data']]
        players = '\n'.join(playerList)

    serverName = serverData['data']['attributes']['name']
    serverStats = serverData['data']['attributes']['status']
    serverMission = serverData['data']['attributes']['details']['mission']
    activePlayer = serverData['data']['attributes']['players']
    maxPlayer = serverData['data']['attributes']['maxPlayers']
    
    embed = discord.Embed(title=serverName, description=serverStats.title(), color=0x00ff00)
    embed.set_thumbnail(url='https://units.arma3.com/groups/img/32641/06EvpC7yf0.png')
    
    if serverStats == 'online':
        embed.add_field(name="Mission", value=serverMission, inline=True)
        embed.add_field(name="Players", value=f'{activePlayer}/{maxPlayer}', inline=True)
        embed.add_field(name="Active Players", value=players, inline=False)
    
    elif serverStats == 'dead' or serverStats == 'removed':
        capture_message(f'{serverName} is {serverStats}')

    return embed


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.command(pass_context=True)
async def serverstats(ctx, serverNumber:int=None):
    if ctx.message.channel.id == settings.channelId:
        if serverNumber == 1 or serverNumber == 4:
            server = serverList[serverNumber]
            serverData = await getData(f'https://api.battlemetrics.com/servers/{server}', params=None)
            
            if serverData is None:
                await client.say(f'An error has occured, please contact {settings.authorId}')
            
            else:
                playerData = await getData('https://api.battlemetrics.com/players', params={'filter[servers]':server, 
                    'filter[online]':'true', 'page[size]':serverData['data']['attributes']['maxPlayers']})
                embed = await embify(serverData, playerData)
                await client.say(embed=embed)
        
        else:
            await client.say('`Usage: !serverstats [server number] (only server 1 and 4 are supported)`')

if __name__ == '__main__':
    client.run(settings.discordToken)
    