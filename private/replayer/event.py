from datetime import timedelta

from match.fact_match import FactMatch
from summoner.fact_team import FactTeamId
from tools import lazy_property


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
                if (((kill.timestamp - last_kill.timestamp) <= timeout)
                        and
                        (kill.killer == last_kill.killer)):
                    current_row.append(kill)
                else:
                    # create new row
                    rows.append([kill])
            last_kill = kill
    return rows


def get_kill_index(kill, kills):
    for index, s_kill in enumerate(kills):
        if s_kill == kill:
            return index


def generate_events(fact_match: FactMatch):
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
    _PREPEND_TIMEOUT = timedelta(seconds=5)
    _POSTPEND_TIMEOUT = timedelta(seconds=10)
    for event in events:
        companion_ids = event.companion_ids
        ## pre
        current_idx = get_kill_index(event.first_kill, kills)
        kill_time_base = kills[current_idx].timestamp
        companion_kills_pre = []
        while current_idx > 0:
            current_idx = current_idx - 1
            candidate = kills[current_idx]
            time_distance = (kill_time_base - candidate.timestamp)
            if time_distance <= _PREPEND_TIMEOUT:
                for comp_id in candidate.companion_ids:
                    if comp_id in companion_ids:
                        companion_kills_pre.insert(0, candidate)
                        kill_time_base = candidate.timestamp
                        break
            else:
                break
        event.companion_kills_pre = companion_kills_pre
        ## post
        current_idx = get_kill_index(event.last_kill, kills)
        kill_time_base = kills[current_idx].timestamp
        companion_kills_post = []
        while current_idx < (len(kills) - 1):
            current_idx = current_idx + 1
            candidate = kills[current_idx]
            time_distance = (candidate.timestamp - kill_time_base)
            if time_distance <= _POSTPEND_TIMEOUT:
                for comp_id in candidate.companion_ids:
                    if comp_id in companion_ids:
                        companion_kills_post.append(candidate)
                        kill_time_base = candidate.timestamp
                        break
            else:
                break
        event.companion_kills_post = companion_kills_post
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
    companion_kills_pre = []
    companion_kills_post = []
    raw_events = []


class EventKillRow(Event):
    kills_in_row = 0

    def __init__(self, kill_row):
        self._events = kill_row

    @property
    def first_kill(self):
        return self._events[0]

    @property
    def last_kill(self):
        return self._events[-1]

    @lazy_property
    def length(self):
        return self.end_time - self.start_time

    @lazy_property
    def start_time(self):
        if len(self.companion_kills_pre) == 0:
            return self.first_kill.timestamp
        else:
            return self.companion_kills_pre[0].timestamp

    @lazy_property
    def end_time(self):
        if len(self.companion_kills_post) == 0:
            return self.last_kill.timestamp
        else:
            return self.companion_kills_post[-1].timestamp

    @property
    def main_summoner(self):
        return self.first_kill.killer

    @lazy_property
    def victims(self):
        victims = []
        for kill in self._events:
            victims.append(kill.victim)
        return victims

    @lazy_property
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

    @lazy_property
    def companion_ids(self):
        companion_ids = []
        for kill in self._events:
            companion_ids.extend(kill.companion_ids)
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
