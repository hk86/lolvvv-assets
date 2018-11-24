from datetime import timedelta

from match.fact_match import FactMatch
from summoner.fact_team import FactTeamId
from database.kill import Kill
from pprint import pprint

def get_kill_rows(kills):
    kills.sort(key=lambda x: x.timestamp)
    last_kill = None
    rows = []
    if len(kills) > 0:
        rows.append([kills[0]])
        for kill in kills:
            if last_kill:
                current_row = rows[-1]
                # "The act of killing several
                # champions within 10 seconds
                # of each other (30 seconds to
                # Penta Kill after a Quadra Kill
                # if no enemy respawns)."
                if len(current_row) == 4:
                    timeout = timedelta(seconds=30)
                else:
                    timeout = timedelta(seconds=10)
                if (((kill.timestamp - last_kill.timestamp) < timeout)
                    and
                    (kill.killer == last_kill.killer)):
                    current_row.append(kill)
                else:
                    # create new row
                    rows.append([kill])
            last_kill = kill
    return rows

def generate_events(fact_match:FactMatch):
    kills = fact_match.get_kills()
    kills = list(filter(lambda x: x.killer, kills))
    blue_kills = list(filter(lambda x: x.killer.team == FactTeamId.BLUE, kills))
    red_kills = list(filter(lambda x: x.killer.team == FactTeamId.RED, kills))
    rows = (get_kill_rows(blue_kills) + get_kill_rows(red_kills))
    rows.sort(key=lambda x: x[0].timestamp)
    event_kill_row_classes = [EventTripleKill,
        EventQuadraKill, EventPentaKill]
    events = []
    for row in rows:
        for event_kill_row_class in event_kill_row_classes:
            if len(row) == event_kill_row_class.kills_in_row:
                events.append(event_kill_row_class(row))
    return events

class Event:
    platform_id = ''
    game_id = 0
    ev_type = ''
    start_time = timedelta()
    length = timedelta()
    main_summoner = None
    participants = []
    victims = []

    def __hash__(self):
        return hash((
            self.platform_id,
            self.game_id,
            self.event.ev_type,
            self.event.start_time.total_seconds()))

class EventKillRow(Event):
    kills_in_row = 0

    def __init__(self, kill_row):
        self.start_time = kill_row[0].timestamp
        self.length = kill_row[-1].timestamp - kill_row[0].timestamp
        self.main_summoner = kill_row[0].killer
        for kill in kill_row:
            self.participants += kill.participants
            self.victims.append(kill.victim)
        self.participants = list(set(self.participants))

class EventTripleKill(EventKillRow):
    kills_in_row = 3
    ev_type = 'TRIPLEKILL'

class EventQuadraKill(EventKillRow):
    kills_in_row = 4
    ev_type = 'QUADRAKILL'
    
class EventPentaKill(EventKillRow):
    kills_in_row = 5
    ev_type = 'PENTAKILL'
