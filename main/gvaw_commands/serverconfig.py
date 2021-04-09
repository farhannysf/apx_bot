import utility


async def server_configLogic(
    ctx,
    discordEmbed,
    firestore,
    db,
    channelId,
    guildId,
    operation,
    serverTitle,
    serverId,
):
    channelList = utility.retrieveDb_data(db, option="channel-list", title=guildId)
    channelVerify = await utility.checkChannel(
        db, firestore, channelList, channelId, guildId
    )

    if channelVerify:
        serverList = utility.retrieveDb_data(db, option="server-list", title=guildId)
        serverlistDb = db.collection("server-list").document(str(guildId))
        await utility.checkDb(db, serverList, serverlistDb, firestore)

        usageMessage = "`!serverconfig update [name] [IP address]`\n\n`!serverconfig update [name-dcs] [IP address]`\n\n`!serverconfig delete [name]`\n------"
        embed = discordEmbed(
            title="GvAW Server Config",
            description="Assign or remove ArmA 3/DCS servers to the bot.\n\nDCS servers must have -dcs suffix on its name",
            color=0xE74C3C,
        )

        embed.set_thumbnail(url=utility.gvawLogo_url)
        embed.add_field(name="__Usage__", value=usageMessage)

        if operation == "delete":
            if serverTitle is None:
                return await ctx.send(embed=embed)
            data = {str(serverTitle.replace("-", "")): firestore.DELETE_FIELD}
            serverlistDb.update(data)
            return await ctx.send(
                f"**Updated server list.**\n `Deleted: {serverTitle}`"
            )

        if operation == "update":
            if serverTitle is None or serverId is None:
                return await ctx.send(embed=embed)

            from ipaddress import ip_address

            try:
                ip_address(serverId)

            except ValueError as e:
                return await ctx.send(f"`ERROR: {e}.`")

            data = {
                serverTitle.replace("-", ""): {
                    "name": str(serverTitle),
                    "id": str(serverId),
                }
            }
            serverlistDb.update(data)
            return await ctx.send(
                f"**Updated server list.**\n `Name: {serverTitle} (IP: {serverId})`"
            )

        else:
            return await ctx.send(embed=embed)
    else:
        return await ctx.send(
            "`This channel is not authorized. Use !channelconfig to authorize channels.`"
        )
