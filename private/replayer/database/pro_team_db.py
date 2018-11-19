from .meteor import Meteor
from .pro_team import ProTeam

class ProTeamDb:
    def __init__(self, meteor_db: Meteor):
        self._meteor_db = meteor_db

    def get_pro_team(self, team_id: int):
        if team_id > 0:
            static_data = self._meteor_db.get_db_team(team_id)
            return ProTeam(static_data)