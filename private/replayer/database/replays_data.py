from match.replay import Replay
from .database import Database
from .replay_service import ReplayService

from bson import Binary

class ReplaysData(Database, ReplayService):

    def __init__(self, uri_replays_data):
        Database.__init__(self, uri_replays_data)
        self._matches = self._db['replaydata']['matches']

    def init_replay(self, replay:Replay):
        match = {
            'gameId': replay.game_id,
            'platformId': replay.platform_id,
            'metas':{},
            'gameDataChunks':[],
            'keyFrames':[]}
        self._matches.insert_one(match)

    def add_data_chunk(self, replay:Replay, chunk_id, data_chunk):
        # ToDo: save the chunk_id
        self._push_binary_data(replay, 'gameDataChunks', data_chunk)
        
    def add_key_frame(self, replay:Replay, key_frame_id, key_frame):
        # ToDo: save the key_frame_id
        self._push_binary_data(replay, 'keyFrames', key_frame)

    def set_metas(self, replay:Replay, metas):
        game_id = replay.game_id
        platform_id = replay.platform_id
        self._matches.update_one(
            {'$and': [{'gameId': game_id}, {'platformId': platform_id}]},
            {'$set': {'metas': metas}})

    def delete_replay(self, replay:Replay):
        game_id = replay.game_id
        platform_id = replay.platform_id
        self._matches.delete_one(
            {'$and': [{'gameId': game_id}, {'platformId': platform_id}]})

    def check_exists(self, game_id, platform_id):
        if self._matches.count({'$and':
                [{'gameId': game_id}, {'platformId': platform_id}]}) > 0:
            return True
        else:
            return False

    def _push_binary_data(self, replay:Replay, array_name, binary_data):
        game_id = replay.game_id
        platform_id = replay.platform_id
        self._matches.update_one(
            {'$and': [{'gameId': game_id}, {'platformId': platform_id}]},
            {'$push':{array_name: Binary(binary_data)}}, upsert=True)