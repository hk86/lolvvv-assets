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
                event = event_kill_row_class(row)
                event.platform_id = fact_match.platform_id
                event.game_id = fact_match.game_id
                event.match_patch = fact_match.version
                events.append(event)
    return events

class Event:
    platform_id = ''
    game_id = 0
    match_patch = ''
    ev_type = ''
    start_time = timedelta()
    length = timedelta()
    main_summoner = None
    participants = []
    victims = []
    companion_events = []
    raw_events = []

class EventKillRow(Event):
    kills_in_row = 0

    def __init__(self, kill_row):
        self._events = kill_row

    @property
    def length(self):
        return self._events[-1].timestamp - self._events[0].timestamp

    @property
    def start_time(self):
        return self._events[0].timestamp

    @property
    def main_summoner(self):
        return self._events[0].killer

    @property
    def victims(self):
        victims = []
        for kill in self._events:
            victims.append(kill.victim)
        return victims

    @property
    def participants(self):
        participants = []
        for kill in self._events:
            participants += kill.participants
        return list(set(participants))

    @property
    def raw_events(self):
        events = []
        for kill in self._events:
            events.append(kill.event)
        return events

    @property
    def companion_ids(self):
        companion_ids = []
        for kill in self.raw_events:
            companion_ids.append(kill['victimId'])
            companion_ids.extend(kill['assistingParticipantIds'])
        return list(set(companion_ids))

class EventTripleKill(EventKillRow):
    kills_in_row = 3
    ev_type = 'TRIPLEKILL'

class EventQuadraKill(EventKillRow):
    kills_in_row = 4
    ev_type = 'QUADRAKILL'
    
class EventPentaKill(EventKillRow):
    kills_in_row = 5
    ev_type = 'PENTAKILL'
