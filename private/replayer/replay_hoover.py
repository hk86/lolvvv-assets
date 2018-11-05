from database.replay_files import ReplayFiles
from database.meteor import Meteor
from database.live_match_db import LiveMatchGenerator
from match.replay import Replay
from match.live_match import LiveMatch
from replay_downloader import ReplayDownloader

from datetime import timedelta
from time import sleep

YOUNGER_THAN_MIN = 2

if __name__ == "__main__":
    print('start')
    meteor_db = Meteor('mongodb://root:ZTgh67gth1@10.8.0.2:27017/meteor?authSource=admin')
    live_match_service = LiveMatchGenerator(meteor_db)
    replay_service = ReplayFiles()
    #db = Database('mongodb://root:ZTgh67gth1@172.31.92.174:27017/meteor?authSource=admin')
    while True:
        new_live_matches = live_match_service.get_new_live_matches(
            timedelta(minutes=YOUNGER_THAN_MIN))
        for live_match in new_live_matches:
            downloader = ReplayDownloader(replay_service)
            downloader.download(live_match)
        print('sleep')
        sleep(10)
