from os import path
from pprint import pprint

from database.fact_db import FactDataDb
from database.meteor import Meteor
from database.clip_store_service import ClipStoreService
from database.static_pro_db import StaticProDb
from database.static_champ_db import StaticChampDb
from database.pro_team_db import ProTeamDb
from summoner.static_pro import StaticPro
from summoner.fact_perks import FactPerks
from replay_manager import ReplayManager
from event import Event, generate_events
from clip import Clip
from obs import ObsClips

meteor_db = None

def summoners_to_pros(summoners, static_pro_db):
    pros = []
    for summoner in summoners:
        pro = static_pro_db.get_static_pro(
            summoner.account_id,
            summoner.platform_id
        )
        if pro:
            pros.append(pro)
    return pros

if __name__ == '__main__':
    print('start')
    fact_db = FactDataDb('mongodb://10.8.0.1:27017')
    meteor_db = Meteor('mongodb://root:ZTgh67gth1@10.8.0.2:27017/meteor?authSource=admin')
    clip_store = ClipStoreService(meteor_db)
    static_pro_db = StaticProDb(meteor_db)
    static_champ_db = StaticChampDb(meteor_db)
    pro_team_db = ProTeamDb(meteor_db)
    obs = ObsClips()
    replays = ReplayManager()
    replays = replays.get_pending_replays()
    main_video_folder = r'./replays/clips'
    event_counter = 0
    clip_counter = 0
    print('replays counted')
    for replay in replays:
        fact_match = fact_db.get_fact_match(
            replay.game_id,
            replay.platform_id
        )
        events = generate_events(fact_match)
        clips = []
        for event in events:
            event_counter += 1
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
                clip.participant_pros = summoners_to_pros(
                    event.participants, static_pro_db
                )
                clip.victim_pros = summoners_to_pros(
                    event.victims, static_pro_db
                )
                clips.append(clip)
        if (len(clips) > 0):
            match_video_path = path.join(
                main_video_folder,
                fact_match.platform_id,
                str(fact_match.game_id)
            )
            #start lol
            for idx, clip in enumerate(clips):
                clip_counter += 1
                event_num = idx + 1
                clip_folder = path.join(match_video_path,
                                    fact_match.platform_id,
                                    str(fact_match.game_id),
                                    str(event_num))
                obs.show_pregame_overlay(True)
                killer_summoner = clip.event.main_summoner
                killer_stats = (killer_summoner.get_fact_stats())
                obs.set_perks(FactPerks(killer_stats))
                obs.set_champion(static_champ_db.get_champ_key(
                    killer_summoner.get_champ_id()))
                obs.set_main_pro(clip.main_pro)
                pro_team = pro_team_db.get_pro_team(clip.main_pro.team_id)
                obs.set_pro_team(pro_team)
                obs.set_fact_team(killer_summoner.team)
                exit()
                #Path(clip_folder).mkdir(parents=True, exist_ok=True)
                # lol timeshift to event time
                # lol focus on event.main_pro
                clip.ingame_event_num = event_num
                #clip.clip_path = glob(path.join(clip_folder, '*.*'))[0]
                #s3 upload clip
                clip_store.store(clip)
    print('replays: {} events: {} clips: {}'.format(len(replays), event_counter, clip_counter))


    