from os import path
from pprint import pprint

from database.fact_db import FactDataDb
from database.meteor import Meteor
from database.clip_store_service import ClipStoreService
from database.static_pro_db import StaticProDb
from summoner.static_pro import StaticPro
from replay_manager import ReplayManager
from event import Event, generate_events, EventType
from clip import Clip

meteor_db = None

if __name__ == '__main__':
    fact_db = FactDataDb('mongodb://10.8.0.1:27017')
    meteor_db = Meteor('mongodb://root:ZTgh67gth1@10.8.0.2:27017/meteor?authSource=admin')
    clip_store = ClipStoreService(meteor_db)
    static_pro_db = StaticProDb(meteor_db)
    replays = ReplayManager()
    replays = replays.get_pending_replays()
    main_video_folder = r'./replays/clips'
    print('replay num {}'.format(len(replays)))
    for replay in replays:
        fact_match = fact_db.get_fact_match(
            replay.game_id,
            replay.platform_id
        )
        events = generate_events(fact_match)
        print('event num {}'.format(len(events)))
        clips = []
        for event in events:
            main_pro = static_pro_db.get_static_pro(
                event.main_summoner.account_id,
                event.main_summoner.platform_id
            )
            if main_pro:
                clip = Clip()
                clip.game_id = fact_match.game_id
                clip.platform_id = fact_match.platform_id
                clip.event = event
                clip.main_pro = main_pro
                clips.append(clip)
        print('clips {}'.format(len(clips)))
        if (len(clips) > 0):
            match_video_path = path.join(
                main_video_folder,
                fact_match.platform_id,
                str(fact_match.game_id)
            )
            #start lol
            for idx, clip in enumerate(clips):
                event_num = idx + 1
                clip_folder = path.join(match_video_path,
                                    fact_match.platform_id,
                                    str(fact_match.game_id),
                                    str(event_num))
                #Path(clip_folder).mkdir(parents=True, exist_ok=True)
                # lol timeshift to event time
                # lol focus on event.main_pro
                clip.ingame_event_num = event_num
                #clip.clip_path = glob(path.join(clip_folder, '*.*'))[0]
                #s3 upload clip
                clip_store.store(clip)


    