from match import Match
from ReplayDownloader import ReplayDownloader

from threading import Thread
import logging
import json
from time import sleep

class Replay(Match, Thread):

    def __init__(self, live_match, replay_db):
        Match.__init__(
            self, live_match.platform_id,
            live_match.game_id, live_match.encryption_key)
        Thread.__init__(self)
        self._meteor_db = live_match.meteor_db
        self._live_match = live_match
        self._replay_db = replay_db
        self._metas = None
        logging.basicConfig(
            level=logging.WARN,
            format='(%(threadName)-10s) %(message)s',
        )

    def download(self):
        self.start()

    def run(self):
        logging.debug('running')
        self._replay_db.init_replay(self)
        try:
            downloader = ReplayDownloader(self)
            self._set_state('downloading')
            downloader.download()
            state = downloader.state()
        except Exception as err:
            logging.warning('Error: {}'.format(err), exc_info=True)
            self._replay_db.delete_replay(self)
            state = 'failed'
        logging.debug('id: {} plat_id: {} STATE: {}'.format(
            self.game_id, self.platform_id, state))
        self._set_state(state)

    def add_key_frame(self, key_frame_id, key_frame):
        self._replay_db.add_key_frame(self, key_frame_id, key_frame.content)

    def add_chunk(self, chunk_id, chunk):
        self._replay_db.add_data_chunk(self, chunk_id, chunk.content)

    def last_chunk_infos(self, infos):
        pass

    def metas_set(self, metas):
        self._metas = metas
        self._replay_db.set_metas(self, metas)

    def end_stats_set(self, end_stats):
        pass

    def _set_state(self, status: str):
        self._meteor_db.set_replay_status(self, status)

    def _live_match_get(self):
        return self._live_match

    metas = property(fset=metas_set)
    end_stats = property(fset=end_stats_set)
    live_match = property(fget=_live_match_get)
