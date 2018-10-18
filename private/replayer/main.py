from datetime import timedelta, datetime
from pprint import pprint
from os import path
from pathlib import Path
from time import sleep

from database.fact_db import FactDataDb
from database.player import MatchTeam
from kill_row import KillRow
from LoL import LeagueOfLegends, LoLState
from obs import Obs
from tools import get_valid_filename

def get_kill_rows(kills, min_kills_in_row):
    rows = []
    kills_in_row = []
    last_kill = None
    timeout = timedelta(seconds=10)
    kills.sort(key=lambda x: x.timestamp)
    for kill in kills:
        if last_kill:
            if ((last_kill.killer != kill.killer) or
                ((kill.timestamp - last_kill.timestamp) > timeout)
                ):
                if (len(kills_in_row) >= min_kills_in_row):
                    rows.append(KillRow(kills_in_row))
                kills_in_row = []
        kills_in_row.append(kill)
        last_kill = kill
    return rows

if __name__ == "__main__":
    fact_db = FactDataDb('mongodb://10.8.0.1:27017')
    lol = LeagueOfLegends()
    obs = Obs()
    main_video_folder = r'./replays/clips'
    game_id = 3370687081
    platform_id = 'KR'
    encryption_key = 'hS3uz9iDyOAzTdjU9leQDYHmjVtveXg4'
    url = '127.0.0.1:1337'
    match = fact_db.get_fact_match(game_id, platform_id)
    kills = match.get_kills()
    blue_kills = list(filter(lambda x: x.killer.team == MatchTeam.BLUE, kills))
    red_kills = list(filter(lambda x: x.killer.team == MatchTeam.RED, kills))
    min_kills_in_row = KillRow.DOUBLE_KILL
    rows = (get_kill_rows(blue_kills, min_kills_in_row) +
            get_kill_rows(red_kills, min_kills_in_row))
    rows.sort(key=lambda x: x.first_kill_ingame_time())
    if (len(rows) > 0):
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
        print('replay loaded finished')
        print('backjump to start')
        lol.specate_timeshift(timedelta(minutes=-1))
        ingame_time = timedelta(seconds=0)
        #for row in rows:
        row = rows[0]
        ingame_timestamp = row.first_kill_ingame_time()
        print('jumping to {}'.format(ingame_timestamp))
        ingame_time += lol.specate_timeshift(ingame_timestamp)
        ingame_time += lol.specate_timeshift(timedelta(seconds=-15))
        start_record = datetime.now()
        clip_path = path.join(match_video_path,
                              get_valid_filename(str(row.first_kill_ingame_time())))
        Path(clip_path).mkdir(parents=True, exist_ok=True)
        obs.set_recording_folder(clip_path)
        #focus on killer
        obs.start_recording()
        RECORDING_OVERTIME_S = 25
        sleep(row.kill_row_time().total_seconds() +
              RECORDING_OVERTIME_S)
        obs.stop_recording()
        #find video
        ingame_time += (datetime.now() - start_record)
        #start video upload to s3


    print('end')
    