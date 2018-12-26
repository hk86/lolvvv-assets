from datetime import timedelta

from pprint import pprint

from summoner.fact_player import FactPlayer

class Kill:
    def __init__(self, fact_event, fact_match):
        self._fact_event = fact_event
        self._fact_match = fact_match
        
    def _get_timestamp(self):
        return timedelta(seconds=self._fact_event['timestamp']/1000)

    def _get_killer(self):
        if self._fact_event['killerId'] > 0:
            return FactPlayer(
                self._fact_match,
                self._fact_event['killerId'])

    def _get_victim(self):
        return FactPlayer(
            self._fact_match,
            self._fact_event['victimId'])

    def _get_participants(self):
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

    timestamp = property(fget=_get_timestamp)
    killer = property(fget=_get_killer)
    victim = property(fget=_get_victim)
    participants = property(fget=_get_participants)