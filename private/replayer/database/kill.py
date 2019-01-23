from datetime import timedelta
from json import dumps

from summoner.fact_player import FactPlayer
from tools import lazy_property


class Kill:
    def __init__(self, fact_event, fact_match):
        self._fact_event = fact_event
        self._fact_match = fact_match

    @property
    def companion_ids(self):
        companion_ids = [self._fact_event['killerId'], self._fact_event['victimId']]
        companion_ids.extend(self._fact_event['assistingParticipantIds'])
        return companion_ids

    @lazy_property
    def timestamp(self):
        return timedelta(seconds=self._fact_event['timestamp'] / 1000)

    @lazy_property
    def killer_p_id(self):  # participant id
        return self._fact_event['killerId']

    @lazy_property
    def killer(self):
        if self.killer_p_id > 0:
            return FactPlayer(
                self._fact_match,
                self._fact_event['killerId'])

    @lazy_property
    def victim(self):
        return FactPlayer(
            self._fact_match,
            self._fact_event['victimId'])

    @property
    def participants(self):
        participants = []
        for participant in self._fact_event['assistingParticipantIds']:
            participants.append(FactPlayer(
                self._fact_match,
                participant
            ))
        return participants

    @property
    def event(self):
        return self._fact_event

    def __hash__(self):
        return hash(dumps(self._fact_event))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)
