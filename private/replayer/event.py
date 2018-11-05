from datetime import timedelta

from match.fact_match import FactMatch
from summoner.fact_team import FactTeamId
from kill_row import KillRow
from pprint import pprint

def get_kill_rows(kills, min_kills_in_row):
    rows = []
    kills_in_row = []
    last_kill = None
    timeout = timedelta(seconds=10)
    kills.sort(key=lambda x: x.timestamp)
    for kill in kills:
        if last_kill:
            if (((kill.timestamp - last_kill.timestamp) > timeout)
                or
                (last_kill.killer != kill.killer)):
                if (len(kills_in_row) >= min_kills_in_row):
                    rows.append(KillRow(kills_in_row))
                kills_in_row = []
        kills_in_row.append(kill)
        last_kill = kill
    return rows

def generate_events(fact_match:FactMatch):
    kills = fact_match.get_kills()
    kills = list(filter(lambda x: x.killer, kills))
    blue_kills = list(filter(lambda x: x.killer.team == FactTeamId.BLUE, kills))
    red_kills = list(filter(lambda x: x.killer.team == FactTeamId.RED, kills))
    min_kills_in_row = EventType.TRIPPLE_KILL
    rows = (get_kill_rows(blue_kills, min_kills_in_row) +
        get_kill_rows(red_kills, min_kills_in_row))
    rows.sort(key=lambda x: x.first_kill_ingame_time())
    events = []
    for row in rows:
        event = Event()
        event.ev_type = row.row_length()
        event.start_time = row.first_kill_ingame_time()
        event.length = row.kill_row_time()
        event.main_summoner = row.killer()
        events.append(event)
    return events

class EventType:
    UNKOWN = 0
    SINGLE_KILL = 1
    DOUBLE_KILL = 2
    TRIPPLE_KILL = 3
    QUADRA_KILL = 4
    PENTA_KILL = 5
    STRING = [
        None
        , 'SINGLE_KILL'
        , 'DOUBLE_KILL'
        , 'TRIPLE_KILL'
        , 'QUADRA_KILL'
        , 'PENTA_KILL'
    ]

class Event:
    ev_type = EventType.UNKOWN
    start_time = timedelta()
    length = timedelta()
    main_summoner = None
    participants = []
