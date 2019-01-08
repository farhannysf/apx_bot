from os import environ
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

discordToken = environ['discordToken']
channelId = environ['channelId']
authorId = environ['authorId']