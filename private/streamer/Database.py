import time
from threading import Thread

import pprint
import pymongo

class Database:

    def __init__(self, uriMeteor):
        mc = pymongo.MongoClient(uriMeteor)
        self.db = mc['meteor']
        self.active_matches = self.db['fact_active_matches']
        self.streamed_matches = self.db['fact_streamed_matches']


    def getTopRatedLiveMatch(self):
        match = self.active_matches.find_one({'$and': [{'gameStartTime': {'$gt': 0}},
                                                       {'gameLength':{'$gt': 0}}]},
                                              sort=[('ranking', pymongo.DESCENDING), ('gameLength', pymongo.ASCENDING)])
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
        match = {'platformId':platformId,
            'gameId': gameId,
            'streamGameStarting':int(time.time()),
            'streamGameEnding':0,
            'scannedForEvents':False}
        self.streamed_matches.insert_one(match)
        server_state = self.db['dim_server_state']
        server_state.update_one({}, {'$set': {'streaming': {'platformId': platformId, 'gameId': gameId} }})

    def setStreamingMatchEnd(self, gameId, platformId):
       self.streamed_matches.update_one({'$and': [{'gameId': gameId},
                                              {'platformId':platformId}]}, {
                                                '$set': {'streamGameEnding': int(time.time())}})

    def getChampionName(self, champId):
        return self.db['static_champions'].find_one({'id':champId})['name']

    def getPro(self, proId):
        return self.db['static_pros'].find_one({'proId':proId})

    def _getTeam(self, teamId):
        return self.db['static_teams'].find_one({'teamId':teamId})

    def getTeamName(self, teamId):
        return self._getTeam['teamName']

    def getTeamTag(self, teamId):
        return self._getTeam['teamTag']

    def _extractTwitterId(self, pro):
        return pro['social']['twitter']

    def getTwitterId(self, proId):
        return self._extractTwitterId(self.getPro(proId))

    def getAllTwitterIds(self):
        twitterPros = self.db['static_pros'].find({'social.twitter':{'$ne':None}})
        twitterIds = []
        for pro in twitterPros:
            twitterIds.append(self._extractTwitterId(pro))
        return twitterIds
