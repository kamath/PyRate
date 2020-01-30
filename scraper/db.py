import pymongo
import json
import os

class DB:
    def __init__(self):
        mongo_uri = json.loads(open(os.path.join('input', 'mongo.json'), 'r').read())['MONGO_CONNECTION_URI']
        self.client = pymongo.MongoClient(mongo_uri)

