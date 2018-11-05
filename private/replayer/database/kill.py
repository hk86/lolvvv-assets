from datetime import timedelta

from pprint import pprint

from summoner.fact_player import FactPlayer

class Kill:
    def __init__(self, fact_event, fact_match):
        self._ingame_timestamp = timedelta(
            seconds=fact_event['timestamp']/1000)
        self._fact_match = fact_match
        if fact_event['killerId'] == 0:
            with open(r'killer_0.json', 'w') as log_file:
                pprint(fact_event, log_file)
        if fact_event['killerId'] > 0:
            self._killer = FactPlayer(fact_match, fact_event['killerId'])
        else:
            self._killer = None

    def _get_timestamp(self):
        return self._ingame_timestamp

    def _get_killer(self):
        return self._killer

    timestamp = property(fget=_get_timestamp)
    killer = property(fget=_get_killer)