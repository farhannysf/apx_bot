from os import environ
from dotenv import load_dotenv, find_dotenv

def retrieveKeys(db):
    users_ref = db.collection(u'keys')
    docs = users_ref.get()
    for doc in docs:
        return doc.to_dict()   

load_dotenv(find_dotenv())

# discordToken = environ['discordToken']
# channelId = environ['channelId']
# authorId = environ['authorId']
# sentryUrl = environ['sentryUrl']
# segmentKey = environ['segmentKey']