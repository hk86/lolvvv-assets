import pprint
import pymongo

class Database:

    def __init__(self, uriMeteor, uriStatic):
        mc = pymongo.MongoClient(uriMeteor)
        self.db = mc['meteor']
        self.staticDb = pymongo.MongoClient(uriStatic)['staticdata']
        self.active_matches = self.db['fact_active_matches']


    def getTopRatedLiveMatch(self):
        match = self.active_matches.find_one({'$and': [{'gameStartTime': {'$gt': 0}},
                                                       {'gameLength':{'$gt': 0}}]},
                                              sort=[('ranking', pymongo.DESCENDING)])
        return match

    def matchStillRunning(self, gameId, platformId):
        if self.active_matches.find({'$and': [{'gameId': gameId},
                                              {'platformId':platformId}]}).count() > 0:
            return True
        else:
            return False

    def getMatch(self, gameId, platformId):
        return self.db['fact_matches'].find_one({'$and': [{'gameId': gameId},
                                                          {'platformId':platformId}]})

    def setStreamingParams(self, gameId, platformId):
        server_state = self.db['dim_server_state']
        server_state.update_one({}, {'$set': {'streaming': {'platformId': platformId, 'gameId': gameId} }})

    def getChampionName(self, champId):
        return self.staticDb['static_champions'].find_one({'id':champId})['name']

    def getPro(self, proId):
        return self.staticDb['static_pros'].find_one({'proId':proId})

    def getTeamName(self, teamId):
        return self.staticDb['static_teams'].find_one({'teamId':teamId})['teamName']

    def getTeamTag(self, temaId):
        return self.staticDb['static_teams'].find_one({'teamId':teamId})['teamTag']
