from .database import Database

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
            {'marked': {'$exists': False}}
            ]})
        matches = []
        for db_match in found_matches:
            matches.append(db_match)
            self._active_matches.update_one({'$and':
                [{'gameId': db_match['gameId']},{'platformId':db_match['platformId']}]},
                                           {'$set': {'marked': True}})
        return matches

    def get_db_match(self, platform_id: str, game_id: int):
        return self._fact_replays.find_one(
            {'$and': [{'gameId': game_id},{'platformId':platform_id}]})

    def set_replay_status(self, game_id: int, platform_id: str, status:str):
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
                'status': status}
            self._fact_replays.insert_one(replay_match)

    def get_fact_replay(self, game_id: int, platform_id: str):
        return self._fact_replays.find_one({'$and': [{'gameId': game_id},
                    {'platformId':platform_id}]})

    def get_replay_status(self, game_id: int, platform_id: str):
        replay = self.get_db_replay(game_id, platform_id)
        if replay:
            return replay['status']

    def delete_replay(self, game_id: int, platform_id: str):
        self._fact_replays.delete_one({'$and': [{'gameId': game_id},
                    {'platformId':platform_id}]})

    def get_all_replays(self):
        return self._fact_replays.find({})

    def get_pro(self, account_id: int, platform_id: str):
        platform_pros = list(
            filter(lambda x: ((platform_id in x['accounts'])),
            self._cached_pros)
            )
        for pro in platform_pros:
            for pro_id in pro['accounts'][platform_id]:
                    if pro_id == account_id:
                        return pro

    def store_clip_entry(self, clip_entry):
        pprint(clip_entry)
        # ToDo: in die Datenbank schreiben
        # self._fact_clips.insert_one(clip_entry)