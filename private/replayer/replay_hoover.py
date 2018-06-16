import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'streamer'))

from Database import Database
from Replay import Replay
from database.replays_data import ReplaysData

from datetime import timedelta
from time import sleep

YOUNGER_THAN_MIN = 2

if __name__ == "__main__":
    print('start')
    #db = Database('mongodb://root:ZTgh67gth1@10.8.0.10:27017/meteor?authSource=admin')
    #replays_db = ReplaysData('mongodb://ec2-18-205-163-9.compute-1.amazonaws.com:27017')
    db = Database('mongodb://root:ZTgh67gth1@172.31.92.174:27017/meteor?authSource=admin')
    replays_db = ReplaysData('mongodb://127.0.0.1:27017')
    while True:
        new_live_matches = db.get_new_live_matches(timedelta(minutes=YOUNGER_THAN_MIN))
        for live_match in new_live_matches:
            replay = Replay(live_match, replays_db)
            replay.download()
        print('going sleep')
        sleep(30)
