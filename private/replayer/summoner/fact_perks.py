class FactPerks(object):

    def __init__(self, fact_player_stats):
        self._rune1_0 = fact_player_stats['perkPrimaryStyle']
        self._rune1_1 = fact_player_stats['perk0']
        self._rune1_2 = fact_player_stats['perk1']
        self._rune1_3 = fact_player_stats['perk2']
        self._rune1_4 = fact_player_stats['perk3']
        self._rune2_0 = fact_player_stats['perkSubStyle']
        self._rune2_1 = fact_player_stats['perk4']
        self._rune2_2 = fact_player_stats['perk5']

    @property
    def rune1_0(self): 
        return self._rune1_0
        
    @property
    def rune1_1(self): 
        return self._rune1_1
        
    @property
    def rune1_2(self): 
        return self._rune1_2
        
    @property
    def rune1_3(self): 
        return self._rune1_3
        
    @property
    def rune1_4(self): 
        return self._rune1_4
        
    @property
    def rune2_0(self): 
        return self._rune2_0
        
    @property
    def rune2_1(self): 
        return self._rune2_1
        
    @property
    def rune2_2(self): 
        return self._rune2_2
