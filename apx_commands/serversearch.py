import utility

async def server_searchLogic(ctx, firestore, db, author, channelId, guildId, serverTitle, capture_message):
    channelList = utility.retrieveDb_data(db, option='channellist', title=guildId)
    channelVerify = await utility.checkChannel(db, firestore, channelList, channelId, guildId)

    if channelVerify:
        try:
            serverData = await utility.getData(f'https://api.battlemetrics.com/servers', params={'filter[search]':serverTitle, 'filter[game]':'arma3'}, capture_message=capture_message)
        except TypeError:
            return await ctx.send(f'**Usage:**\n\n`!serversearch "server name"`')
            
        if serverData is None:
            return await ctx.send(f'An error has occured, please contact {author}')
        
        else:
            if not serverData['data']:
                return await ctx.send('No server found.')

            searchResult = await utility.search_resultFormat(serverData)
            await ctx.send(searchResult)

            if serverData['links']:
                while True:
                    def check(msg):
                        return msg.author == ctx.message.author
                    try:
                        link = serverData['links']['next']
                    except KeyError:
                        break

                    await ctx.send('Send "!nextsearch" to browse more or send "!quitsearch" to quit.')
                    msg = await ctx.bot.wait_for('message', check=check)

                    if msg.content == '!quitsearch':
                        break
                   
                    elif msg.content == '!nextsearch':
                        serverData = await utility.getData(link, params=None, capture_message=capture_message)
                        searchResult = await utility.search_resultFormat(serverData)
                        await ctx.send(searchResult)

            return await ctx.send('Search completed.')

    else:
        return await ctx.send('`This channel is not authorized. Use !channelconfig to authorize channels.`')