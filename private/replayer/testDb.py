from os import path
from pprint import pprint

from database.fact_db import FactDataDb
from database.meteor import Meteor
from database.static_pro_db import StaticProDb
from database.clip_store_service import ClipStoreService
from replay_manager import ReplayManager
from event import Event, generate_events
from clip_recorder import ClipRecorder
from clip import Clip
from LoL import LeagueOfLegends
from s3_clip_upload import S3ClipUpload

if __name__ == '__main__':
    #init
    print('start')
    fact_db = FactDataDb('mongodb://10.8.0.1:27017')
    meteor_db = Meteor('mongodb://root:ZTgh67gth1@10.8.0.2:27017/meteor?authSource=admin')
    clip_store = ClipStoreService(meteor_db)
    static_pro_db = StaticProDb(meteor_db)
    replay_manager = ReplayManager()
    lol = LeagueOfLegends()
    recorder = ClipRecorder(meteor_db, lol)
    store_service = S3ClipUpload(meteor_db)
    #run
    replays = replay_manager.get_pending_replays()
    print('replays counted')
    for replay in replays:
        fact_match = fact_db.get_fact_match(
            replay.game_id,
            replay.platform_id
        )
        events = generate_events(fact_match)
        clips = recorder.record_clips(events, replay)
        for clip in clips:
            store_service.upload(clip)
    print('replays: {} events: {} clips: {}'.format(len(replays), event_counter, clip_counter))


    