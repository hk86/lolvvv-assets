class Match(object):
    def __init__(self, platform_id, game_id):
        self._GAME_ID = game_id
        self._PLATFORM_ID = platform_id

    def _get_platform_id(self):
        return self._PLATFORM_ID

    def _get_game_id(self):
        return self._GAME_ID

    platform_id = property(fget=_get_platform_id)
    game_id = property(fget=_get_game_id)