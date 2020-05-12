from . import match
from .spectate import Spectate


class SpectateMatch(match.Match, Spectate):

    def __init__(self, platform_id, game_id, encryption_key, url):
        match.Match.__init__(self, platform_id, game_id)
        Spectate.__init__(self, encryption_key, url)
