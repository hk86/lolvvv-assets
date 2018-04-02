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
        self._server_state = self.db['dim_server_state']

        self._cachePro = None
        self._cacheChamp = None
        self._cacheTeam = None


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
        self._server_state.update_one({}, {'$set': {'streaming': {'platformId': platformId, 'gameId': gameId} }})

    def setStreamingMatchEnd(self, gameId, platformId):
       self.streamed_matches.update_one({'$and': [{'gameId': gameId},
                                              {'platformId':platformId}]}, {
                                                '$set': {'streamGameEnding': int(time.time())}})

    def _getChampion(self, champId):
        if (self._cacheChamp == None) or (self._cacheChamp['id'] != champId):
            self._cacheChamp = self.db['static_champions'].find_one({'id':champId})

        return self._cacheChamp

    def getChampionName(self, champId):
        return self._getChampion(champId)['name']

    def getChampionKey(self, champId):
        return self._getChampion(champId)['key']

    def getPro(self, proId):
        if (self._cachePro == None) or (self._cachePro['proId'] != proId):
            self._cachePro = self.db['static_pros'].find_one({'proId':proId})
        return self._cachePro

    def getProKey(self, proId):
        return self.getPro(proId)['key']

    def _getTeam(self, teamId):
        if (self._cacheTeam == None) or (self._cacheTeam['teamId'] != teamId):
            self._cacheTeam = self.db['static_teams'].find_one({'teamId':teamId})

        return self._cacheTeam

    def getTeamName(self, teamId):
        return self._getTeam(teamId)['teamName']

    def getTeamTag(self, teamId):
        return self._getTeam(teamId)['teamTag']

    def _extractTwitterId(self, pro):
        return pro['social']['twitter']

    def getTwitterId(self, proId):
        return self._extractTwitterId(self.getPro(proId))

    def _getProByTwitterId(self, twitterId):
        if (self._cachePro == None) or (self._cachePro['social']['twitter'] != twitterId):
            self._cachePro = self.db['static_pros'].find_one({'social.twitter':twitterId})

        return self._cachePro

    def getProIdByTwitterId(self, twitterId):
        return self._getProByTwitterId(twitterId)['proId']

    def getProNicknameByTwitterId(self, twitterId):
        return self._getProByTwitterId(twitterId)['nickName']

    def getAllTwitterIds(self):
        twitterPros = self.db['static_pros'].find({'social.twitter':{'$ne':None}})
        twitterIds = []
        for pro in twitterPros:
            twitterIds.append(self._extractTwitterId(pro))
        return twitterIds

    def getMainTweetId(self):
        return self._server_state.find_one()['twitter']['live']['tweetId']

    def updateMainTweet(self, tweetId):
        self._server_state.update_one({}, {'$set': {{'twitter.live': {'tweetId': tweetId, 'tweetPostedTimestamp': int(time.time())} }} },upsert=False)

    def _createLast24hCriteria(self):
        streamed_matches_24h = self.db['fact_streamed_matches'].find(
            {'streamGameEnding': { '$gt': int(time.time()) - 24*60*60 } },
            { '_id': 0, 'platformId': 1, 'gameId': 1 }
        )
        # Generate a match criteria for the selection from the fact_matches_pro col
        return [match for match in streamed_matches_24h]

    def _getMostPlayedChampsOnStream(self, match_criteria, limit=3):
        stats = []
        pipeline = [
            {'$match': { '$or': match_criteria }},
            {'$group': {
                    '_id': '$participant.championId',
                    'count': {'$sum': 1}
                }},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]
        for aggr in self.db['fact_matches_pro'].aggregate(pipeline):
            champ = self.db['static_champions'].find_one({'language': 'en_US', 'id': aggr['_id']})
            stats.append({
                'championId': aggr['_id'],
                'championKey': champ['key'],
                'championName': champ['name'],
                'count': aggr['count'],
            })
        return stats
    
    def _getMostShownProsOnStream(self, match_criteria, limit=3):
        stats = []
        pipeline = [
            {'$match': { '$or': match_criteria }},
            {'$group': {
                    '_id': '$participantIdentity.pro.proId',
                    'count': {'$sum': 1}
                }},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]
        for aggr in self.db['fact_matches_pro'].aggregate(pipeline):
            pro = self.db['static_pros'].find_one({'proId': aggr['_id']})
            stats.append({
                'proId': aggr['_id'],
                'proKey': pro['key'],
                'proNickName': pro['nickName'],
                'count': aggr['count'],
            })
        return stats

    def getMostPlayedChampsLast24Hours(self, limit=3):
        criteria = self._createLast24hCriteria()
        return self._getMostPlayedChampsOnStream(criteria, limit)

    def getMostShownProLast24Hours(self, limit=3):
        criteria = self._createLast24hCriteria()
        return self._getMostShownProsOnStream(criteria, limit)