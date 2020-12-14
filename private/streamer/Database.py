import time
from datetime import datetime,timedelta,timezone
from threading import Thread
from LiveMatch import LiveMatch
from ClashLiveMatch import ClashLiveMatch

from pprint import pprint
import pymongo

class Database:

    def __init__(self, uriMeteor):
        mc = pymongo.MongoClient(uriMeteor)
        self.db = mc['meteor']
        self.active_matches = self.db['fact_pros_active_matches']
        self.streamed_matches = self.db['fact_streamed_matches']
        self._server_state = self.db['dim_server_state']
        self._fact_replays = self.db['fact_replays']
        self._cachePro = None
        self._cacheChamp = None
        self._cacheTeam = None

    def get_new_live_matches(self, younger_then:timedelta):
        found_matches = self.active_matches.find({'$and': [
            {'gameLength':{'$lt':int(younger_then.total_seconds())}},
            #{'marked': {'$exists': False}}
            ]})
        matches = []
        for match in found_matches:
            matches.append(self._generate_live_match(match))
            self.active_matches.update_one({'$and':
                [{'gameId': match['gameId']},{'platformId':match['platformId']}]},
                                           {'$set': {'marked': True}})
        return matches

    def _generate_live_match(self, match):
        platform_id = match['platformId']
        game_id = match['gameId']
        encryption_key = match['observers']['encryptionKey']
        if match['gameQueueConfigId'] == 700:
            return ClashLiveMatch(platform_id,game_id,encryption_key, self)
        else:
            return LiveMatch(platform_id, game_id, encryption_key, self)

    def getTopRatedLiveMatch(self):
        match = self.active_matches.find_one({'$and': [{'gameStartTime': {'$gt': 0}},
                                                       {'gameLength':{'$gt': 0}}]},
                                              sort=[('ranking', pymongo.DESCENDING), ('gameLength', pymongo.ASCENDING)])
        if match:
            return self._generate_live_match(match)
        else:
            return None

    def matchStillRunning(self, gameId, platformId):
        if self.active_matches.find({'$and': [{'gameId': gameId},
                                              {'platformId':platformId}]}).count() > 0:
            return True
        else:
            return False

    def getMatch(self, gameId, platformId):
        return self.db['fact_pros_matches'].find_one({'$and': [{'gameId': gameId},
                                                          {'platformId':platformId}]})

    def getStreaimedMatchesByTime(self, timeStart, timeStop):
        spectatorOffset=timedelta(minutes=3)
        tmpMatches = self.streamed_matches.find({'$and': [{'streamGameStarting': {'$gte':int((timeStart-spectatorOffset).timestamp())}},
                                             {'streamGameStarting': {'$lt':int(timeStop.timestamp())}},
                                             {'streamGameEnding': {'$gt': 0}}]})
        matches = []
        for match in tmpMatches:
            matches.append({
                'gameId': match['gameId'],
                'platformId': match['platformId']})

        return matches

    def getStreamedMatchTime(self, gameId, platformId):
        match = self.getStreamedMatch(gameId, platformId)
        return ({
            'start': datetime.fromtimestamp(match['streamGameStarting'], timezone.utc),
            'stop': datetime.fromtimestamp(match['streamGameEnding'], timezone.utc)
            })

    def getStreamedMatch(self, gameId, platformId):
        return self.streamed_matches.find_one({'$and': [{'gameId': gameId},
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

    # TODO fact_matches_pro outdated!
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
    
    # TODO fact_matches_pro outdated!
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

    def set_replay_status(self, match, status:str):
        game_id = match._get_game_id()
        platform_id = match._get_platform_id()
        encryption_key = match._get_encryption_key()
        replay_match = self._fact_replays.find_one(
            {'$and': [{'gameId': game_id},{'platformId':platform_id}]})
        if replay_match:
            self._fact_replays.update_one(
                {'$and': [{'gameId': game_id},{'platformId':platform_id}]},
                                          {'$set':  {'status': status}})
        else:
            replay_match = {
                'gameId': game_id,
                'platformId':platform_id,
                'status': status,
                'encryptionKey': encryption_key}
            self._fact_replays.insert_one(replay_match)

    def set_replay_game_version(self, match, game_version):
        game_id = match._get_game_id()
        platform_id = match._get_platform_id()
        encryption_key = match._get_encryption_key()
        replay_match = self._fact_replays.find_one(
            {'$and': [{'gameId': game_id},{'platformId':platform_id}]})
        if replay_match:
            self._fact_replays.update_one(
                {'$and': [{'gameId': game_id},{'platformId':platform_id}]},
                                          {'$set':  {'gameVersion': game_version}})
            
