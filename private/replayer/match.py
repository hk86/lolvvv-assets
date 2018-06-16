import json

class Match:

    def __init__(self, platform_id, game_id, encryption_key):
        PLATFORMS = json.load(open(r'../json/LolPlatforms.json'))
        match_platform = PLATFORMS[platform_id]
        self._URL = match_platform['domain'] + ':' + match_platform['port']
        self._GAME_ID = game_id
        self._ENCRYPTION_KEY = encryption_key
        self._PLATFORM_ID = platform_id

    def _get_platform_id(self):
        return self._PLATFORM_ID

    def _get_game_id(self):
        return self._GAME_ID

    def _get_encryption_key(self):
        return self._ENCRYPTION_KEY

    def _get_url(self):
        return self._URL

    platform_id = property(fget=_get_platform_id)
    game_id = property(fget=_get_game_id)
    encryption_key = property(fget=_get_encryption_key)
    url = property(fget=_get_url)