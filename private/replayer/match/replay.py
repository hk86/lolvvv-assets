from match.spectate_match import SpectateMatch


class Replay(SpectateMatch):

    def __init__(self, platform_id, game_id, encryption_key, url, record_timestamp):
        SpectateMatch.__init__(self, platform_id, game_id, encryption_key, url)
        self._record_timestamp = record_timestamp

    @property
    def record_timestamp(self):
        return self._record_timestamp
