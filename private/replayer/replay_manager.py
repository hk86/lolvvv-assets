from os import path
from glob import glob
from json import load as json_load
from shutil import rmtree
from random import getrandbits

from match.replay import Replay
from replay_server import ReplayServer

class ReplayManager:
    _URL = '127.0.0.1:1337'
    _PLATFORM_IDS = {
        'KR'
        #, 'NA1'
        #, 'EUW1'
    }

    def __init__(self, replays_path='replays'):
        self._REPLAY_PATH = replays_path

    def get_pending_replays(self):
        replays = []
        for platform in self._PLATFORM_IDS:
            platform_path = path.join(self._REPLAY_PATH, platform)
            if path.exists(platform_path):
                game_paths = glob(path.join(platform_path, '*'))
                game_ids = []
                for game_path in game_paths:
                    game_ids.append(path.basename(game_path))
                for game_id in game_ids:
                    metas_path = path.join(
                                        platform_path
                                        , game_id
                                        , 'metas.json'
                                        )
                    if path.exists(metas_path):
                        metas = json_load(open(metas_path))
                        match = Replay(
                            int(game_id),
                            platform,
                            metas['encryptionKey'],
                            self._URL + '-' + str(getrandbits(32)))
                        replays.append(match)
        return replays

    def mark_as_handled_rep(self, platform_id, game_id):
        replay_path = path.join(
                            self._REPLAY_PATH
                            , platform_id
                            , str(game_id)
                            )
        if path.exists(replay_path):
            rmtree(replay_path)
