from database.player import Player

class FactPlayer(Player):

    def __init__(self, fact_match, participant_id):
        fact_player = fact_match.get_fact_player(participant_id)
        fact_participant = fact_match.get_participant(participant_id)
        Player.__init__(
            self,
            fact_player['currentAccountId'],
            fact_player['currentPlatformId'],
            fact_participant['teamId'])

    
