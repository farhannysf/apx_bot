import utility

async def server_configLogic(ctx, firestore, db, channelId, guildId, operation, serverTitle, serverId):
    channelList = utility.retrieveDb_data(db, option='channel-list', title=guildId)
    channelVerify = await utility.checkChannel(db, firestore, channelList, channelId, guildId)

    if channelVerify:
        serverList = utility.retrieveDb_data(db, option='server-list', title=guildId)
        serverlistDb = db.collection('server-list').document(str(guildId))
        await utility.checkDb(db, serverList, serverlistDb,firestore)
        
        usageMessage = '**Usage:**\n\n`!serverconfig update [name] [battlmetrics server id]\n!serverconfig delete [name]`'

        if operation == 'delete':
            if serverTitle is None: 
                return await ctx.send(usageMessage)
            data = {str(serverTitle): firestore.DELETE_FIELD}
            serverlistDb.update(data)
            return await ctx.send(f'**Updated server list.**\n `Deleted Server {serverTitle}`')

        if operation == 'update':
            if serverTitle is None or serverId is None:
                return await ctx.send(usageMessage)
            
            data = {str(guildId):{str(serverTitle):str(serverId)}}
            serverlistDb.update(data)
            return await ctx.send(f'**Updated server list.**\n `Server {serverTitle} (Battlemetrics ID: {serverId})`')
        
        else:
            return await ctx.send(usageMessage)
    else:
        return await ctx.send('`This channel is not authorized. Use !channelconfig to authorize channels.`')