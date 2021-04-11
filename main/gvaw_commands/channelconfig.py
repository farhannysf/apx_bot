import re
import utility


async def channel_configLogic(
    ctx,
    verify_channel,
    discordEmbed,
    firestore,
    db,
    channelId,
    guildId,
    operation,
    channel,
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
                verify_channel = verify_channel(channelSelect)
                if not verify_channel:
                    raise AttributeError

            except AttributeError:
                return await ctx.send(
                    f"Please input the correct channel format, e.g. `#example`."
                )

            if operation == "authorize":
                try:
                    channelList[str(channelSelect)]
                except Exception as ex:
                    if ex.args[0] == str(channelSelect):
                        data = {str(channelSelect): str(channelSelect)}
                        channellist_Db.update(data)
                        return await ctx.send(
                            f"**Updated authorized channel list.**\n <#{channelSelect}> `is now authorized`"
                        )
                return await ctx.send(
                    f"Error: <#{channelSelect}> is already authorized."
                )

            if operation == "revoke":
                try:
                    channelList[str(channelSelect)]
                except Exception as ex:
                    if ex.args[0] == str(channelSelect):
                        return await ctx.send(
                            f"ERROR: <#{channelSelect}> is not authorized yet."
                        )
                    else:
                        return await ctx.send(f"ERROR")

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
    embed.add_field(name="__Usage__", value=usageMessage)
    embed.add_field(
        name="__Authorized Channels__", value=f"{authorizedChannels}\n------"
    )
    return await ctx.send(embed=embed)