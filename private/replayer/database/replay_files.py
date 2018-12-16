from match.spectate_match import SpectateMatch
from .replay_service import ReplayService

from os import path
from shutil import rmtree
import pathlib
import json

class ReplayFiles(ReplayService):
    def __init__(self, replays_path='replays'):
        self._REPLAYS_PATH = replays_path
        # CONSTANTS
        self._KEY_FRAME_FOLDER = 'keyFrame'
        self._DATA_CHUNK_FOLDER = 'gameDataChunk'

    def init_replay(self, replay:SpectateMatch):
        replay_path = self._get_replay_path(replay)
        self._create_folder(replay_path, self._DATA_CHUNK_FOLDER)
        self._create_folder(replay_path, self._KEY_FRAME_FOLDER)

    def add_key_frame(self, replay:SpectateMatch, key_frame_id, key_frame):
        self._save_octet_stream(replay, self._KEY_FRAME_FOLDER,
                                key_frame_id, key_frame)

    def add_data_chunk(self, replay:SpectateMatch, chunk_id, data_chunk):
        self._save_octet_stream(replay, self._DATA_CHUNK_FOLDER,
                                chunk_id, data_chunk)

    def set_metas(self, replay:SpectateMatch, metas):
        wr_path = path.join(self._get_replay_path(replay),'metas.json')
        with open(wr_path, 'w') as outfile:
            json.dump(metas, outfile)

    def delete_replay(self, replay:SpectateMatch):
        rmtree(self._get_replay_path(SpectateMatch))

    def _get_replay_path(self, replay:SpectateMatch):
        return path.join(self._REPLAYS_PATH, replay.platform_id,
                         str(replay.game_id))

    def _create_folder(self, replay_path, folder_name):
        created_path = path.join(replay_path, folder_name)
        pathlib.Path(created_path).mkdir(parents=True, exist_ok=True)
        return created_path

    def _save_octet_stream(self, replay:SpectateMatch,
                           folder_name, id, binary_data):
        wr_path = path.join(self._get_replay_path(replay),
                        folder_name, str(id))
        with open(wr_path, 'wb') as f:
            f.write(binary_data)
