from os import environ
from dotenv import load_dotenv, find_dotenv

def retrievegit Keys(db):
    users_ref = db.collection(u'keys')
    docs = users_ref.get()
    for doc in docs:
        return doc.to_dict()   

load_dotenv(find_dotenv())