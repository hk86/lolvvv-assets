class Match(object):
    def __init__(self, platform_id, game_id):
        self._GAME_ID = game_id
        self._PLATFORM_ID = platform_id

    def _get_platform_id(self):
        return self._PLATFORM_ID

    def _get_game_id(self):
        return self._GAME_ID

    def __eq__(self, other):
        return (
            (self._GAME_ID == other.game_id)
            and
            (self._PLATFORM_ID == other.platform_id)
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    platform_id = property(fget=_get_platform_id)
    game_id = property(fget=_get_game_id)