from .match import Match

from database.kill import Kill

class FactMatch(Match):
    def __init__(self, platform_id, game_id, fact_data):
        super().__init__(platform_id, game_id)
        self._MATCH_DATA = fact_data

    def get_kills(self):
        kills = []
        for frame in self._MATCH_DATA['timeline']['frames']:
            for event in frame['events']:
                if event['type'] == 'CHAMPION_KILL':
                    kills.append(Kill(event, self))
        return kills

    def get_team_kills(self, team_id):
        kills = self.get_kills()
        kills_for_team = []
        for kill in kills:
            if (kill.killer.team == team_id):
                kills_for_team.append(kill)
        return kills_for_team

    def get_fact_player(self, participant_id):
        for participant_identity in (
            self._MATCH_DATA['participantIdentities']):
            if (participant_identity['participantId']
                ==
                participant_id):
                return participant_identity['player']

    def get_participant(self, participant_id):
        for participant in self._MATCH_DATA['participants']:
            if participant['participantId'] == participant_id:
                return participant
