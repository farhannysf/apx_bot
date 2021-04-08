import utility
import json


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

        dcsCheck = serverList[serverTitle.replace("-", "")]["name"].split("-")
        if dcsCheck[-1] == "dcs":
            from main import keys

            dcsKeys = {
                "DCS_USERNAME": keys["DCS_USERNAME"],
                "DCS_PASSWORD": keys["DCS_PASSWORD"],
            }
            serverUrl = "https://www.digitalcombatsimulator.com/en/auth/"
            servers_body = await utility.getDCS_data(
                serverUrl, params=None, key=dcsKeys, capture_message=capture_message
            )
            servers = json.loads(servers_body)
            serverIndex = next(
                (
                    index
                    for (index, d) in enumerate(servers["SERVERS"])
                    if d["IP_ADDRESS"] == "101.50.3.86"
                ),
                None,
            )
            server = servers["SERVERS"][serverIndex]
            serverStats = "online"

            if serverStats == "online":
                serverName = server["NAME"]
                serverIP = server["IP_ADDRESS"]
                serverPort = server["PORT"]
                scenario = server["MISSION_NAME"]
                scenarioUptime = server["MISSION_TIME_FORMATTED"]
                players = server["PLAYERS"]
                maxPlayers = server["PLAYERS_MAX"]

                embed = discordEmbed(
                    title=serverName, description=serverStats.title(), color=0x00FF00
                )
                embed.set_thumbnail(url=utility.gvawLogo_url)
                embed.add_field(
                    name="IP Address", value=f"{serverIP}:{serverPort}", inline=False
                )
                embed.add_field(name="Scenario", value=scenario, inline=False)
                embed.add_field(name="Uptime", value=scenarioUptime, inline=False)
                embed.add_field(
                    name="Players",
                    value=f"{players}/{maxPlayers}",
                    inline=True,
                )
                # WIP
                return await ctx.send(embed=embed)

            elif serverStats == "offline":
                message = f"{dcsCheck[-1]} is {serverStats}"
                capture_message(message)

                return await ctx.send(message)

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
