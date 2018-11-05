from database.meteor import Meteor
from summoner.fact_team import FactTeamId

class TeamGenerator:
    def __init__(self, meteor_db: Meteor):
        self._meteor_db = meteor_db

    def get_team(self, platform_id, game_id, team_id: FactTeamId):
