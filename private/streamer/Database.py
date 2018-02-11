import pprint
import pymongo

class Database:

    def __init__(self, uri):
        mc = pymongo.MongoClient(uri)
        self.db = mc['meteor']
        self.active_matches = self.db['fact_active_matches']


    def getTopRatedLiveMatch(self):
        match = self.active_matches.find_one({'platformId':{'$in':['EUW1','NA1']}}, sort=[('gameLength', 1)])
        return match

    def matchStillRunning(self, gameId):
        if self.active_matches.find({'gameId': gameId}).count() > 0:
            return True
        else:
            return False

    def getMatch(self, gameId):
        return self.db['fact_matches'].find_one({'gameId':gameId})

    def setStreamingParams(self, gameId, platformId):
        pass

