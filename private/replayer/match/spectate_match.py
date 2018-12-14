from .match import Match
from .spectate import Spectate

class SpectateMatch(Match, Spectate):

    def __init__(self, platform_id, game_id, encryption_key, url):
        Match.__init__(self, platform_id, game_id)
        Spectate.__init__(self, encryption_key, url)