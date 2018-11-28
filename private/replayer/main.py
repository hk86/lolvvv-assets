from os import path, system
from datetime import datetime, timedelta
from pprint import pprint
from time import sleep

from database.fact_db import FactDataDb
from database.meteor import Meteor
from database.static_pro_db import StaticProDb
from database.clip_store_service import ClipStoreService
from replay_manager import ReplayManager
from replay_hoover import ReplayHoover
from event import Event, generate_events
from clip_recorder import ClipRecorder
from clip import Clip
from LoL import LeagueOfLegends
from patch_version import PatchVersion
from s3_clip_upload import S3ClipUpload
from logger import Logger

def upgrade_lol(lol: LeagueOfLegends, meteor_db:Meteor):
    lol.start_update()
    lol.wait_for_update()
    lol.stop_update()
    lol = LeagueOfLegends()
    meteor_db.set_patch_version(lol.version(),
        meteor_db.get_current_server_patch(lol.UPDATE_PLATFORM))

if __name__ == '__main__':
    #init
    logger = Logger('clipper')
    logger.warn('start')
    exit()
    start_time = datetime.now()
    fact_db = FactDataDb('mongodb://10.8.0.1:27017')
    meteor_db = Meteor('mongodb://root:ZTgh67gth1@10.8.0.2:27017/meteor?authSource=admin')
    clip_store = ClipStoreService(meteor_db)
    static_pro_db = StaticProDb(meteor_db)
    patch_version = PatchVersion(meteor_db)
    replay_manager = ReplayManager()
    lol = LeagueOfLegends()
    playable_patch = patch_version.client_patch(lol.version)
    if not playable_patch:
        upgrade_lol(lol, meteor_db)
        playable_patch = patch_version.client_patch(lol.version)
    recorder = ClipRecorder(meteor_db, lol)
    store_service = S3ClipUpload(meteor_db)
    replay_hover = ReplayHoover(meteor_db)
    replay_hover.start()
    MIN_RUNTIME = timedelta(hours=8)
    try:
        while True:
            replays = replay_manager.get_pending_replays()
            fact_matches = []
            for replay in replays:
                fact_match = fact_db.get_fact_match(
                    replay.game_id,
                    replay.platform_id
                )
                if fact_match:
                    fact_matches.append(fact_match)
            patch_matches = []
            for idx, match in enumerate(fact_matches):
                match_patch = patch_version.version_to_patch(match.version)
                if (match_patch
                    ==
                    playable_patch):
                    patch_matches.append(fact_match)
                else:
                    # na hoffentlich klappt das so
                    if match_patch < playable_patch:
                        fact_matches.pop(idx)
                        """
                        replay_manager.mark_as_handled_rep(
                            match.platform_id,
                            match.game_id
                        )
                        """
            if ((len(patch_matches) > 0)
                for match in patch_matches:
                    events = generate_events(match)
                    clips = recorder.record_clips(events, replay)
                    for clip in clips:
                        store_service.upload(clip)
                    """
                    replay_manager.mark_as_handled_rep(
                        replay.platform_id,
                        replay.game_id
                    )
                    """
            elif ((len(fact_matches) > 0) 
                and (patch_version.version_to_patch(
                    meteor_db.get_current_server_patch(
                        lol.UPDATE_PLATFORM)
                    )
                )):
                upgrade_lol(lol, meteor_db)
                playable_patch = patch_version.client_patch(lol.version)
            if (datetime.now()-start_time) > MIN_RUNTIME:
                if replay_hover.get_num_downloads_in_progress() == 0:
                    break
            sleep(60)
    except Exception as err:
        logger.error('Error: {}'.format(err), exc_info=True)
    finally:
        for handler in logger.handlers:
            handler.close()
            logger.removeFilter(handler)
        replay_hover.stop()
        # reboot
        #system('shutdown -t 1 -r -f')


    