from datetime import timedelta

from database.fact_player import FactPlayer

class Kill:
    def __init__(self, event, fact_match):
        self._kill_event = event
        self._ingame_timestamp = timedelta(
            seconds=event['timestamp']/1000)
        self._fact_match = fact_match
        self._killer = FactPlayer(fact_match, event['killerId'])

    def _get_timestamp(self):
        return self._ingame_timestamp

    def _get_killer(self):
        return self._killer

    timestamp = property(fget=_get_timestamp)
    killer = property(fget=_get_killer)