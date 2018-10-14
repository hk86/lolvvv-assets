from database.summoner import Summoner

class MatchTeam:
    BLUE = 100
    RED = 200

class Player(Summoner):
    
    def __init__(self, account_id, platform_id, team_id: MatchTeam):
        Summoner.__init__(self, account_id, platform_id)
        self._TEAM = team_id

    def _get_team(self):
        return self._TEAM
        
    team = property(fget=_get_team)