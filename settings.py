import aiohttp

from os import environ
from dotenv import load_dotenv, find_dotenv

async def asyncGet(*args, **kwargs):
    async with aiohttp.ClientSession() as client:
        async with client.get(*args, **kwargs) as response:
            response.body = await response.read()

            return response

async def getData(url, params, capture_message):
    response = await asyncGet(url, params=params)
    
    if response.status == 200:
        data = await response.json()
        return data    
    else:
        capture_message(f'Battlemetrics API: {response.status}')
    
async def embify(serverData, playerData, discordEmbed, capture_message):
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
    
    embed = discordEmbed(title=serverName, description=serverStats.title(), color=0x00ff00)
    embed.set_thumbnail(url='https://units.arma3.com/groups/img/32641/06EvpC7yf0.png')
    
    if serverStats == 'online':
        embed.add_field(name="Mission", value=serverMission, inline=True)
        embed.add_field(name="Players", value=f'{activePlayer}/{maxPlayer}', inline=True)
        embed.add_field(name="Active Players", value=players, inline=False)
    
    elif serverStats == 'dead' or serverStats == 'removed':
        capture_message(f'{serverName} is {serverStats}')

    return embed

def retrieveData(db, option, title):
    data_ref = db.collection(option).document(title)
    docs = data_ref.get()
    return docs.to_dict()   

async def checkDb(db, serverlistDb, ctx, firestore):
    serverList = retrieveData(db, option='serverlist', title=ctx.message.channel.id)
    if serverList is None:
        data = {'create':'create'}
        serverlistDb.set(data)
        serverlistDb.update({'create':firestore.DELETE_FIELD})
        return

load_dotenv(find_dotenv())