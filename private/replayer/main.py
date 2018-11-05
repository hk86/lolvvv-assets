from datetime import timedelta, datetime
from pprint import pprint
from os import path
from pathlib import Path
from time import sleep
from glob import glob

from database.fact_db import FactDataDb
from database.player import MatchTeam
from kill_row import KillRow
from LoL import LeagueOfLegends, LoLState
#from obs import Obs
from clip import Clip
from event import Event, generate_events
from tools import get_valid_filename

if __name__ == "__main__":
    fact_db = FactDataDb('mongodb://10.8.0.1:27017')
    lol = LeagueOfLegends()
    #obs = Obs()
    main_video_folder = r'./replays/clips'
    game_id = 3370687081
    platform_id = 'KR'
    encryption_key = 'hS3uz9iDyOAzTdjU9leQDYHmjVtveXg4'
    url = '127.0.0.1:1337'
    match = fact_db.get_fact_match(game_id, platform_id)
    events = generate_events(match)
    if (len(events) > 0):
        match_video_path = path.join(
            main_video_folder,
            platform_id,
            str(game_id)
            )
        START_TRIES = 3
        for x in range(0, START_TRIES):
            lol.start_spectate(url, game_id, platform_id, encryption_key)
            lol.wait_for_replay_start()
            if (lol.check_running() == LoLState.UNKNOWN):
                break
            lol.stop_lol()
            if (x == START_TRIES-1):
                # ToDo: was soll hier geschehen?
                pass
        lol.modify_ui()
        lol.specate_timeshift(timedelta(minutes=-1))
        ingame_time = timedelta(seconds=0)
        for idx, event in enumerate(events):
            event_num = idx + 1
            timeshift = event.start_time - ingame_time
            ingame_time += lol.specate_timeshift(timeshift)
            ingame_time += lol.specate_timeshift(timedelta(seconds=-15))
            start_record = datetime.now()
            clip_folder = path.join(match_video_path,
                                get_valid_filename(str(event_num)))
            Path(clip_folder).mkdir(parents=True, exist_ok=True)
            #obs.set_recording_folder(clip_folder)
            killer = event.main_pro
            lol.focus_player(killer.team, killer.get_inteam_idx)
            #obs.start_recording()
            RECORDING_OVERTIME_S = 25
            sleep(event.start_time.total_seconds() +
                RECORDING_OVERTIME_S)
            #obs.stop_recording()
            clip_path = glob(path.join(clip_folder, '*.*'))[0]
            clip = Clip()
            clip.platform_id = match.platform_id
            clip.game_id = match.game_id
            clip.clip_path = clip_path
            clip.ingame_event_num = event_num
            clip.event = event
            #start video upload to s3
            ingame_time += (datetime.now() - start_record)
        lol.stop_lol()


    print('end')
    