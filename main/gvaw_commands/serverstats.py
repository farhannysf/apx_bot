import utility
import json
from asyncio import TimeoutError as async_TimeOutError


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
            serverIP = serverList[serverTitle.replace("-", "")]["id"].split(":")

        except (KeyError, AttributeError):
            availableServers = "\n".join(
                "{} (IP: {})".format(value["name"], value["id"])
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
            embed.add_field(name="__Usage__", value=usageMessage)
            embed.add_field(
                name="__Available Servers__", value=f"{availableServers}\n------"
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
                    if d["IP_ADDRESS"] == serverIP[0]
                ),
                None,
            )

            if serverIndex == None:
                serverStats = "offline"
                return await ctx.send(
                    f"`{serverTitle} ({serverIP[0]}) is {serverStats}.`"
                )

            server = servers["SERVERS"][serverIndex]
            serverStats = "online"
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
                name="__IP Address__", value=f"{serverIP}:{serverPort}", inline=False
            )
            embed.add_field(name="__Scenario__", value=scenario, inline=False)
            embed.add_field(name="__Uptime__", value=scenarioUptime, inline=False)
            embed.add_field(
                name="__Players__",
                value=f"{players}/{maxPlayers}",
                inline=True,
            )

            return await ctx.send(embed=embed)

        from a2s import ainfo

        serverPort = 2303
        if len(serverIP) == 2:
            serverPort = serverIP[1]

        serverAddress = (serverIP[0], serverPort)

        try:
            server = await ainfo(serverAddress)

        except (ConnectionRefusedError, async_TimeOutError):
            serverStats = "offline"
            return await ctx.send(f"`{serverTitle} ({serverIP[0]}) is {serverStats}.`")

        serverStats = "online"

        if serverStats == "online":
            serverName = server.server_name
            serverPort = server.port
            serverMap = server.map_name
            serverMission = server.game
            activePlayers = server.player_count
            maxPlayers = server.max_players

            embed = discordEmbed(
                title=serverName, description=serverStats.title(), color=0x00FF00
            )
            embed.set_thumbnail(url=utility.gvawLogo_url)
            embed.add_field(
                name="__IP Address__", value=f"{serverIP[0]}:{serverPort}", inline=False
            )
            embed.add_field(name="__Map__", value=serverMap, inline=False)
            embed.add_field(name="__Mission__", value=serverMission, inline=False)
            embed.add_field(
                name="__Players__", value=f"{activePlayers}/{maxPlayers}", inline=False
            )

        return await ctx.send(embed=embed)

    else:
        return await ctx.send(
            "`This channel is not authorized. Use !channelconfig to authorize channels.`"
        )
