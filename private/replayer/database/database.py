import pymongo


class Database:

    def __init__(self, uri):
        self._db = pymongo.MongoClient(uri)