from datetime import timedelta

from match.fact_match import FactMatch
from summoner.fact_team import FactTeamId
from database.kill import Kill
from pprint import pprint

def get_kill_rows(kills):
    last_kill = None
    timeout = timedelta(seconds=10)
    kills.sort(key=lambda x: x.timestamp)
    last_kill = None
    rows = []
    if len(kills) > 0:
        rows.append([kills[0]])
        for kill in kills:
            if last_kill:
                if (((kill.timestamp - last_kill.timestamp) < timeout)
                    and
                    (kill.killer == last_kill.killer)):
                    rows[-1].append(kill)
                else:
                    rows.append([kill])
            last_kill = kill
    return rows

def generate_events(fact_match:FactMatch):
    kills = fact_match.get_kills()
    kills = list(filter(lambda x: x.killer, kills))
    blue_kills = list(filter(lambda x: x.killer.team == FactTeamId.BLUE, kills))
    red_kills = list(filter(lambda x: x.killer.team == FactTeamId.RED, kills))
    min_kills_in_row = EventType.TRIPPLE_KILL
    rows = (get_kill_rows(blue_kills) + get_kill_rows(red_kills))
    rows = list(filter(lambda x: len(x) >= min_kills_in_row, rows))
    rows.sort(key=lambda x: x[0].timestamp)
    events = []
    for row in rows:
        event = Event()
        event.ev_type = len(row)
        event.start_time = row[0].timestamp
        event.length = row[-1].timestamp - row[0].timestamp
        event.main_summoner = row[0].killer
        for kill in row:
            event.participants += kill.participants
            event.victims.append(kill.victim)
        event.participants = list(set(event.participants))
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
    victims = []
