import asyncio
import aiohttp
import discord
import settings

client = discord.Client()

async def asyncGet(*args, **kwargs):
    async with aiohttp.ClientSession() as client:
        async with client.get(*args, **kwargs) as response:
            response.body = await response.read()

            return response

async def getData(url, params):
    response = await asyncGet(url, params=params)
    data = await response.json()
    
    return data

async def embify(serverData, playerData):
    serverName = serverData['data']['attributes']['name']
    serverStats = serverData['data']['attributes']['status']
    serverMission = serverData['data']['attributes']['details']['mission']
    activePlayer = serverData['data']['attributes']['players']
    maxPlayer = serverData['data']['attributes']['maxPlayers']

    playerList = [item['attributes']['name'] for item in playerData['data']]
    
    embed = discord.Embed(title=serverName, description=serverStats.title(), color=0x00ff00)
    embed.set_thumbnail(url='https://units.arma3.com/groups/img/32641/06EvpC7yf0.png')
    embed.add_field(name="Mission", value=serverMission, inline=True)
    embed.add_field(name="Players", value=f'{activePlayer}/{maxPlayer}', inline=True)
    embed.add_field(name="Active Players", value='\n'.join(playerList), inline=False)
    
    return embed


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.content.startswith('!serverstats'):
        serverData = await getData('https://api.battlemetrics.com/servers/1015436', params=None)
        if serverData['data']['attributes']['status'] == 'offline':
            await client.send_message(message.channel, 'Server is offline.')
        else:
            playerData = await getData('https://api.battlemetrics.com/players', params={'filter[servers]':'1015436', 'filter[online]':'true', 
                'page[size]':serverData['data']['attributes']['maxPlayers'] })
            embed = await embify(serverData, playerData)
            await client.send_message(message.channel, embed=embed)

if __name__ == '__main__':
    client.run(settings.discordToken)