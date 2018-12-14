from .spectate import Spectate
from .fact_match import FactMatch

class FactReplay(FactMatch, Spectate):
    def __init__(self, fact_match, replay):
        FactMatch = fact_match
        Spectate = replay