import utility


async def server_statsLogic(
    ctx,
    firestore,
    db,
    author,
    channelId,
    guildId,
    serverTitle,
    discordEmbed,
    capture_message,
):
    channelList = utility.retrieveDb_data(db, option="channel-list", title=guildId)
    channelVerify = await utility.checkChannel(
        db, firestore, channelList, channelId, guildId
    )

    if channelVerify:
        serverList = utility.retrieveDb_data(db, option="server-list", title=guildId)

        if serverList is None:
            return await ctx.send(
                "No server is set. Use `!serverconfig` for more info."
            )

        try:
            server = serverList[serverTitle.replace("-", "")]["id"]

        except (KeyError, AttributeError):
            availableServers = "\n".join(
                "{} (Battlemetrics ID: {})".format(value["name"], value["id"])
                for key, value in serverList.items()
            )
            if availableServers == "":
                availableServers = "No server added yet"
            usageMessage = "`!serverstats [name]`\n------"
            embed = discordEmbed(
                title="GvAW Server List",
                description="Check status of a server by the assigned name",
                color=0xE74C3C,
            )

            embed.set_thumbnail(url=utility.gvawLogo_url)
            embed.add_field(name="Usage", value=usageMessage)
            embed.add_field(
                name="Available Servers", value=f"{availableServers}\n------"
            )
            return await ctx.send(embed=embed)

        serverData = await utility.getData(
            f"https://api.battlemetrics.com/servers/{server}",
            params=None,
            capture_message=capture_message,
        )

        if serverData is None:
            return await ctx.send(f"An error has occured, please contact {author}")

        else:
            playerData = await utility.getData(
                "https://api.battlemetrics.com/players",
                params={"filter[servers]": server, "filter[online]": "true"},
                capture_message=capture_message,
            )

            if playerData is None:
                return await ctx.send(f"An error has occured, please contact {author}")

            embed = await utility.embify(
                serverData, playerData, discordEmbed, capture_message
            )
        return await ctx.send(embed=embed)

    else:
        return await ctx.send(
            "`This channel is not authorized. Use !channelconfig to authorize channels.`"
        )
