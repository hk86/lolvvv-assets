from datetime import timedelta
from json import dumps

from pprint import pprint

from summoner.fact_player import FactPlayer

class Kill:
    def __init__(self, fact_event, fact_match):
        self._fact_event = fact_event
        self._fact_match = fact_match
        
    @property
    def companion_ids(self):
        companion_ids = [self._fact_event['killerId']]
        companion_ids.append(self._fact_event['victimId'])
        companion_ids.extend(self._fact_event['assistingParticipantIds'])
        return companion_ids

    @property
    def timestamp(self):
        return timedelta(seconds=self._fact_event['timestamp']/1000)

    @property
    def killer(self):
        if self._fact_event['killerId'] > 0:
            return FactPlayer(
                self._fact_match,
                self._fact_event['killerId'])

    @property
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