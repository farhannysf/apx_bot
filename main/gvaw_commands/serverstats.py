import utility
from bs4 import BeautifulSoup


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
            serverUrl = "https://dcs.glowie.xyz/servers/101.50.3.86:10308"
            serverData_body = await utility.getDCS_data(
                serverUrl, params=None, capture_message=capture_message
            )

            serverData_parsed = BeautifulSoup(serverData_body, "html.parser")
            table = serverData_parsed.table.find_all("td")
            serverStats = "online"
            serverName = table[4].string
            serverIP = table[4].a["href"].split("/")
            scenario = table[1].string.split("(")
            players = table[2].string.split("(")
            embed = discordEmbed(
                title=serverName, description=serverStats.title(), color=0x00FF00
            )
            embed.set_thumbnail(url=utility.gvawLogo_url)

            if serverStats == "online":
                embed.add_field(name="IP Address", value=serverIP[2], inline=False)
                embed.add_field(name="Uptime", value=scenario[1][:-1], inline=False)
                embed.add_field(name="Scenario", value=scenario[0], inline=False)
                embed.add_field(
                    name="Players",
                    value=f"{players[0].replace(' ','')}/{players[1][:-1]}",
                    inline=True,
                )

            elif serverStats == "dead" or serverStats == "removed":
                capture_message(f"{serverName} is {serverStats}")

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
