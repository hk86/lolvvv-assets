from datetime import timedelta

from companion_finder import CompanionPreFinder, CompanionPostFinder
from database.kill import Kill
from match.fact_match import FactMatch
from tools import lazy_property


def get_kill_rows(kills: [Kill]):
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
                if (kill.timestamp - last_kill.timestamp) <= timeout:
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
    rows = []
    for p_id in range(1, 11):  # participant id
        participant_kills = list(filter(lambda x: x.killer_p_id == p_id, kills))
        rows.extend(get_kill_rows(participant_kills))
    event_kill_row_classes = [EventTripleKill,
                              EventQuadraKill,
                              # EventAloneDoubleKill,
                              EventAlonePentaKill,
                              EventAloneTripleKill,
                              EventAloneQuadraKill,
                              EventPentaKill]
    events = []
    for row in rows:
        for event_kill_row_class in event_kill_row_classes:
            event = event_kill_row_class(row)
            companion_ids = event.companion_ids
            event.companion_kills_pre = CompanionPreFinder(kills) \
                .find_companions(event.first_kill, companion_ids)
            event.companion_kills_post = CompanionPostFinder(kills) \
                .find_companions(event.last_kill, companion_ids)
            if event.is_valid:
                event.platform_id = fact_match.platform_id
                event.game_id = fact_match.game_id
                event.match_patch = fact_match.version
                events.append(event)
                break
    events.sort(key=lambda x: x.start_time)
    return events


class Event:
    platform_id = ''
    game_id = 0
    match_patch = ''
    ev_type = ''
    event_based_rec_overtime_s = 0
    start_time = timedelta()
    length = timedelta()
    main_summoner = None
    participants = []
    victims = []
    companion_kills_pre = []
    companion_kills_post = []
    raw_events = []


class EventKillRow(Event):
    event_based_rec_overtime_s = 10
    kills_in_row = 0

    def __init__(self, kill_row):
        self._events = kill_row

    @property
    def is_valid(self):
        if len(self._events) != self.kills_in_row:
            return False
        if len(self.participants) == 0:
            return False
        return True

    @property
    def first_kill(self):
        return self._events[0]

    @property
    def last_kill(self):
        return self._events[-1]

    @lazy_property
    def length(self):
        return self.end_time - self.start_time

    @property
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


class EventAloneKillRow(EventKillRow):
    event_based_rec_overtime_s = 5
    extended_timeout = timedelta(seconds=5)

    @property
    def is_valid(self):
        if len(self.participants) > 0:
            return False
        if len(self._events) < EventAloneTripleKill.kills_in_row:
            return False
        for kill_idx, comp_kill in enumerate(self.companion_kills_post):
            if ((comp_kill.victim == self.main_summoner) and
                    not (comp_kill.killer in self.victims)):
                self._events.append(self.companion_kills_post.pop(kill_idx))
        if len(self._events) != self.kills_in_row:
            return False
        return True


class EventAloneDoubleKill(EventAloneKillRow):
    kills_in_row = 2
    ev_type = '1VS2'


class EventAloneTripleKill(EventTripleKill, EventAloneKillRow):
    ev_type = '1VS3'


class EventAloneQuadraKill(EventTripleKill, EventAloneKillRow):
    ev_type = '1VS4'


class EventAlonePentaKill(EventPentaKill, EventAloneKillRow):
    ev_type = '1VS5'
