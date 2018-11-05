from .spectate_match import SpectateMatch

class Replay(SpectateMatch):
    def __init__(self, game_id, platform_id, encryption_key, url):
        SpectateMatch.__init__(self,
                       platform_id,
                       game_id,
                       encryption_key)
        self._url = url

    def _get_url(self):
        return self._url

    url = property(fget=_get_url)