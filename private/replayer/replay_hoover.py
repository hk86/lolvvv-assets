from database.replay_files import ReplayFiles
from database.meteor import Meteor
from database.live_match_db import LiveMatchGenerator
from match.live_match import LiveMatch
from replay_downloader import ReplayDownloader

from threading import Thread, Event
from datetime import timedelta
from time import sleep

class ReplayHoover(Thread):
    YOUNGER_THAN_MIN = 2
    
    def __init__(self, meteor_db: Meteor):
        Thread.__init__(self)
        self._stop_event = Event()
        self._meteor_db = meteor_db
        self._downloads = []

    def stop(self):
        self._stop_event.set()

    def run(self):
        live_match_service = LiveMatchGenerator(self._meteor_db)
        replay_service = ReplayFiles()
        while not self._stop_event.is_set():
            new_live_matches = live_match_service.get_new_live_matches\
                (timedelta(minutes=self.YOUNGER_THAN_MIN))
            for live_match in new_live_matches:
                downloader = ReplayDownloader(replay_service)
                downloader.download(live_match)
                self._downloads.append(downloader)
            self._cleanup_downloads()
            sleep(10)
        print('waiting for current downloads finished')
        for download in self._downloads:
            download.join()
        print('all downloads finished')

    def get_num_downloads_in_progress(self):
        self._cleanup_downloads()
        return len(self._downloads)
    
    def _cleanup_downloads(self):
        for idx, download in enumerate(self._downloads):
                if not download.is_alive():
                    self._downloads.pop(idx)
