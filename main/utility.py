import aiohttp
import logging

logger = logging.getLogger(__name__)
gvawLogo_url = "https://units.arma3.com/groups/img/165841/ZU3SH51cXb.png"


async def asyncGet(*args, **kwargs):
    async with aiohttp.ClientSession() as client:
        async with client.get(*args, **kwargs) as response:
            response.body = await response.read()

            return response


async def asyncPost(*args, **kwargs):
    async with aiohttp.ClientSession() as client:
        async with client.post(*args, **kwargs) as response:
            response.body = await response.read()

            return response


async def getData(url, params):
    response = await asyncGet(url, params=params)

    if response.status == 200:
        data = await response.json()
        return data

    else:
        logger.error(f"{url}: {response.status}")


async def getDCS_data(url, params, key):
    payload = {
        "AUTH_FORM": "Y",
        "TYPE": "AUTH",
        "backurl": "/en/personal/server/?ajax=y",
        "USER_LOGIN": key["DCS_USERNAME"],
        "USER_PASSWORD": key["DCS_PASSWORD"],
        "USER_REMEMBER": "Y",
    }
    response = await asyncPost(url, data=payload)

    if response.status == 200:
        data = await response.text()
        return data

    else:
        logger.error(f"DCS: {response.status}")


def retrieveDb_data(db, option, title):
    data_ref = db.collection(option).document(title)
    docs = data_ref.get()
    return docs.to_dict()


async def checkDb(db, objectList, objectDb, firestore):
    if objectList is None:
        data = {"create": "create"}
        objectDb.set(data)
        objectDb.update({"create": firestore.DELETE_FIELD})
        return


async def checkChannel(db, firestore, channelList, channelId, guildId):
    channellist_Db = db.collection("channel-list").document(str(guildId))
    await checkDb(db, channelList, channellist_Db, firestore)
    try:
        channelVerify = retrieveDb_data(db, option="channel-list", title=guildId)[
            f"{channelId}"
        ]
    except KeyError:
        return
    return channelVerify


async def search_resultFormat(serverData):
    serverProperties = {
        i["attributes"]["name"]: i["attributes"]["ip"] for i in serverData["data"]
    }
    searchResult = "\n\n".join(
        "{} (IP Address: {})".format(key, value)
        for key, value in serverProperties.items()
    )
    return searchResult