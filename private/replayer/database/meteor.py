from .database import Database
from .static_pro import StaticPro
from match.live_match import LiveMatch
from match.replay import Replay

from datetime import timedelta

from pprint import pprint

class Meteor(Database):

    def __init__(self, uri_meteor_db):
        Database.__init__(self, uri_meteor_db)
        self._meteor = self._db['meteor']
        self._fact_replays = self._meteor['fact_replays']
        self._active_matches = self._meteor['fact_active_matches']
        pro_cursor = self._meteor['static_pros'].find(
            {'accounts': {'$exists': True, '$nin': [None]}})
        self._cached_pros = []
        for pro in pro_cursor:
            self._cached_pros.append(pro)

    def get_new_live_matches(self, younger_then:timedelta):
        found_matches = self._active_matches.find({'$and': [
            {'gameLength':{'$lt':int(younger_then.total_seconds())}},
            #{'marked': {'$exists': False}}
            ]})
        matches = []
        for db_match in found_matches:
            matches.append(self._generate_live_match(db_match))
            self._active_matches.update_one({'$and':
                [{'gameId': db_match['gameId']},{'platformId':db_match['platformId']}]},
                                           {'$set': {'marked': True}})
        return matches

    def get_replay(self, platform_id, game_id):
        db_replay = self._fact_replays.find_one(
            {'$and': [{'gameId': game_id},{'platformId':platform_id}]})
        if db_replay:
            live_match = LiveMatch(platform_id, game_id, db_replay['encryptionKey'], self)
            return Replay(live_match)

    def set_replay_status(self, match:Replay, status:str):
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

    def get_db_replay(self, game_id, platform_id):
        return self._fact_replays.find_one({'$and': [{'gameId': game_id},
                    {'platformId':platform_id}]})

    def get_replay_status(self, game_id, platform_id):
        replay = self.get_db_replay(game_id, platform_id)
        if replay:
            return replay['status']

    def delete_replay(self, game_id, platform_id):
        self._fact_replays.delete_one({'$and': [{'gameId': game_id},
                    {'platformId':platform_id}]})

    def get_all_replays(self):
        return self._fact_replays.find({})

    def get_pro(self, account_id, platform_id):
        platform_pros = list(
            filter(lambda x: ((platform_id in x['accounts'])),
            self._cached_pros)
            )
        for pro in platform_pros:
            for pro_id in pro['accounts'][platform_id]:
                    if pro_id == account_id:
                        return StaticPro(pro)

    def _generate_live_match(self, db_match):
        platform_id = db_match['platformId']
        game_id = db_match['gameId']
        encryption_key = db_match['observers']['encryptionKey']
        if db_match['gameQueueConfigId'] == 700:
            return ClashLiveMatch(platform_id,game_id,encryption_key, self)
        else:
            return LiveMatch(platform_id, game_id, encryption_key, self)