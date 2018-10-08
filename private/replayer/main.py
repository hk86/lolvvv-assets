from datetime import timedelta
from pprint import pprint

from database.fact_db import FactDataDb
from kill_row import KillRow
from LoL import LeagueOfLegends

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
                    for counter, kill in enumerate(kills_in_row):
                        print('counter: {} killerId:{} time: {}'.format(counter, kill.killer, kill.timestamp))
                kills_in_row = []
        kills_in_row.append(kill)
        last_kill = kill
    return rows

if __name__ == "__main__":
    fact_db = FactDataDb('mongodb://10.8.0.1:27017')
    lol = LeagueOfLegends()

    game_id = 3370687081
    platform_id = 'KR'
    encryption_key = 'hS3uz9iDyOAzTdjU9leQDYHmjVtveXg4'
    url = '127.0.0.1:1337'
    
    ingame_kills = fact_db.get_match_kills(game_id, platform_id)
    rows = get_kill_rows(ingame_kills, KillRow.DOUBLE_KILL)
    if (len(rows) > 0):
        lol.start_spectate(url, game_id, platform_id, encryption_key)
        lol.wait_for_replay_start()
        print('replay loaded finished')
        #for row in rows:
        row = rows[0]
        ingame_timestamp = row.first_kill_ingame_time().total_seconds()
        print('jumping to time {}'.format(row.first_kill_ingame_time()))
        print('jumping to seconds {}'.format(ingame_timestamp))
        lol.replay_time_jump(ingame_timestamp)
    print('end')
    