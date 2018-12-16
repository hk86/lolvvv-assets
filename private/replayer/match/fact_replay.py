from match.spectate_match import SpectateMatch
from match.spectate import Spectate
from match.match import Match
from match.fact_match import FactMatch

class FactReplay(FactMatch, Spectate):
    def __init__(self, fact_match: FactMatch, replay:SpectateMatch):
        if (Match(fact_match) != Match(replay)):
            raise BaseException(('fact_match {}/{} and replay {}/{}'+
                'have to be the same.').format(
                    fact_match.platfrom_id, fact_match.game_id,
                    replay.platfrom_id, replay.game_id))

        self.__dict__.update(fact_match.__dict__)
        Spectate.__init__(self, replay.encryption, replay.url)