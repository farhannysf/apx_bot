import utility

async def server_statsLogic(ctx, firestore, db, author, channelId, guildId, serverTitle, discordEmbed, capture_message):
    channelList = utility.retrieveDb_data(db, option='channellist', title=guildId)
    channelVerify = await utility.checkChannel(db, firestore, channelList, channelId, guildId)
    
    if channelVerify:
        serverList = utility.retrieveDb_data(db, option='serverlist', title=guildId)
        
        if serverList is None:
            return await ctx.send('No server is set. Use `!serverconfig` for more info.')

        try:
            server = serverList[str(serverTitle)]
        
        except KeyError:
            availableServers = '\n'.join('{} (Battlemetrics ID: {})'.format(key, value) for key, value in serverList.items())
            return await ctx.send(f'**Usage:**\n\n`!serverstats [server name]`\n\n**Available Servers:**\n\n` {availableServers} `')

        serverData = await utility.getData(f'https://api.battlemetrics.com/servers/{server}', params=None, capture_message=capture_message)
            
        if serverData is None:
            return await ctx.send(f'An error has occured, please contact {author}')
        
        else:
            playerData = await utility.getData('https://api.battlemetrics.com/players', params={'filter[servers]':server, 
                'filter[online]':'true'}, capture_message=capture_message)
            
            if playerData is None:
                return await ctx.send(f'An error has occured, please contact {author}')

            embed = await utility.embify(serverData, playerData, discordEmbed, capture_message)
        return await ctx.send(embed=embed)
    
    else:
        return await ctx.send('`This channel is not authorized. Use !channelconfig to authorize channels.`')