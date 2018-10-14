import json

from .match import Match

class SpectateMatch(Match):

    def __init__(self, platform_id, game_id, encryption_key):
        Match.__init__(self, platform_id, game_id)
        self._ENCRYPTION_KEY = encryption_key

    def _get_encryption_key(self):
        return self._ENCRYPTION_KEY

    def _get_url(self):
        PLATFORMS = json.load(open(r'../json/LolPlatforms.json'))
        match_platform = PLATFORMS[self._PLATFORM_ID]
        return (match_platform['domain'] + ':' + match_platform['port'])

    encryption_key = property(fget=_get_encryption_key)
    url = property(fget=_get_url)