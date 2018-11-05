from abc import ABC, abstractmethod

from .match import Match

class SpectateMatch(Match, ABC):

    def __init__(self, platform_id, game_id, encryption_key):
        Match.__init__(self, platform_id, game_id)
        self._ENCRYPTION_KEY = encryption_key

    def _get_encryption_key(self):
        return self._ENCRYPTION_KEY

    @abstractmethod
    def _get_url(self):
        pass

    encryption_key = property(fget=_get_encryption_key)
    url = property(fget=_get_url)