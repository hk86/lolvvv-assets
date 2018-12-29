from summoner.fact_player import FactPlayer
from summoner.static_pro import StaticPro

class IngamePro(StaticPro, FactPlayer):
    def __init__(self, static_pro: StaticPro, fact_player: FactPlayer):
        self.__dict__.update(static_pro.__dict__)
        self.__dict__.update(fact_player.__dict__)