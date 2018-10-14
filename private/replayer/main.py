from datetime import timedelta
from pprint import pprint
from os import path
from pathlib import Path
from time import sleep

from database.fact_db import FactDataDb
from database.player import MatchTeam
from kill_row import KillRow
from LoL import LeagueOfLegends
from obs import Obs

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
    main_video_folder = r'./replays/videos'
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
        Path(match_video_path).mkdir(parents=True, exist_ok=True)
        obs.set_recording_folder(match_video_path)
        lol.start_spectate(url, game_id, platform_id, encryption_key)
        lol.wait_for_replay_start()
        # check for running
        print('replay loaded finished')
        #for row in rows:
        row = rows[0]
        ingame_timestamp = row.first_kill_ingame_time()
        print('backjump to start')
        lol.specate_timeshift(timedelta(minutes=-1))
        print('jumping to {}'.format(ingame_timestamp))
        lol.specate_timeshift(ingame_timestamp)
        lol.specate_timeshift(timedelta(seconds=-15))
        obs.start_recording()
        #focus on killer
        RECORDING_OVERTIME_S = 25
        sleep(match.kill_row_time.total_seconds() +
              RECORDING_OVERTIME_S)
        obs.stop_recording()
        #find video
        #start video upload to s3


    print('end')
    