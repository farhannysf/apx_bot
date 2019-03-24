import utility

async def server_configLogic(client, firestore, db, channelId, guildId, operation, serverTitle, serverId):
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