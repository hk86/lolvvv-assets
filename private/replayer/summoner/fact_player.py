from summoner.player import Player
from summoner.fact_team import FactTeamId

class FactPlayer(Player):

    def __init__(self, fact_match, participant_id):
        fact_player = fact_match.get_fact_player(participant_id)
        fact_participant = fact_match.get_participant(participant_id)
        Player.__init__(
            self,
            fact_player['currentAccountId'],
            fact_player['currentPlatformId'],
            fact_participant['teamId'])
        self._inteam_idx = participant_id
        if self._get_team() == FactTeamId.RED:
            self._inteam_idx -= 5

    def get_inteam_idx(self):
        return self._inteam_idx
    
