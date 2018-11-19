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

    def stop(self):
        self._stop_event.set()

    def run(self):
        live_match_service = LiveMatchGenerator(self._meteor_db)
        replay_service = ReplayFiles()
        downloads = []
        while not self._stop_event.is_set():
            new_live_matches = live_match_service.get_new_live_matches(
            timedelta(minutes=self.YOUNGER_THAN_MIN))
            for live_match in new_live_matches:
                downloader = ReplayDownloader(replay_service)
                downloader.download(live_match)
                downloads.append(downloader)
            for idx, download in enumerate(downloads):
                if not download.isAlive():
                    downloads.pop(idx)
            sleep(10)
        print('waiting for current downloads finished')
        for download in downloads:
            download.join()
        print('all downloads finished')
