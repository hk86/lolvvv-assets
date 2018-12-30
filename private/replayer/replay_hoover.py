from database.replays_data import ReplaysData
from database.meteor import Meteor
from match.replay import Replay
from match.live_match import LiveMatch
from replay_downloader import ReplayDownloader

from datetime import timedelta
from time import sleep

YOUNGER_THAN_MIN = 0

if __name__ == "__main__":
    print('start')
    meteor_db = Meteor('mongodb://root:ZTgh67gth1@10.8.0.2:27017/meteor?authSource=admin')
    replays_db = ReplaysData('mongodb://ec2-35-169-157-176.compute-1.amazonaws.com:27017')
    #db = Database('mongodb://root:ZTgh67gth1@172.31.92.174:27017/meteor?authSource=admin')
    #replays_db = ReplaysData('mongodb://127.0.0.1:27017')
    #while True:
    new_live_matches = meteor_db.get_new_live_matches(
        timedelta(minutes=YOUNGER_THAN_MIN))
    #for live_match in new_live_matches:
    live_match = new_live_matches[0]
    downloader = ReplayDownloader(replays_db)
    downloader.download(Replay(live_match))
    print('going sleep')
    sleep(1200)
