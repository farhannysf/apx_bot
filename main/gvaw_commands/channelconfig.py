import re
import utility


async def channel_configLogic(
    ctx, discordEmbed, firestore, db, channelId, guildId, operation, channel
):
    channelList = utility.retrieveDb_data(db, option="channel-list", title=guildId)
    await utility.checkChannel(db, firestore, channelList, channelId, guildId)
    authorizedChannels = "\n".join(
        "<#{}>".format(key)
        for key, value in utility.retrieveDb_data(
            db, option="channel-list", title=guildId
        ).items()
    )
    if authorizedChannels == "":
        authorizedChannels = "No channel authorized yet"

    if operation:
        if channel:
            channellist_Db = db.collection("channel-list").document(str(guildId))

            try:
                channelSelect = int(re.search(r"\d+", channel).group())

            except:
                return await ctx.send(
                    "Please input the correct channel format, e.g. `#example`."
                )

            if operation == "authorize":
                data = {str(channelSelect): str(channelSelect)}
                channellist_Db.update(data)
                return await ctx.send(
                    f"**Updated authorized channel list.**\n <#{channelSelect}> `is now authorized`"
                )

            if operation == "revoke":
                data = {str(channelSelect): firestore.DELETE_FIELD}
                channellist_Db.update(data)
                return await ctx.send(
                    f"**Updated authorized channel list.**\n `Revoked access from` <#{channelSelect}>"
                )

    usageMessage = "`!channelconfig authorize #example-channel`\n\n`!channelconfig revoke #example-channel`\n------"
    embed = discordEmbed(
        title="GvAW Channel Config",
        description="Authorize or revoke bot access to channels",
        color=0xE74C3C,
    )

    embed.set_thumbnail(url=utility.gvawLogo_url)
    embed.add_field(name="Usage", value=usageMessage)
    embed.add_field(name="Authorized Channels", value=f"{authorizedChannels}\n------")
    return await ctx.send(embed=embed)