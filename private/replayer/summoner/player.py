from summoner.summoner import Summoner
from summoner.fact_team import FactTeamId

class Player(Summoner):
    
    def __init__(self, account_id, platform_id, team_id: FactTeamId):
        Summoner.__init__(self, account_id, platform_id)
        self._TEAM = team_id

    def _get_team(self):
        return self._TEAM
        
    team = property(fget=_get_team)