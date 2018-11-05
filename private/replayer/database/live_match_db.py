from datetime import timedelta

from database.meteor import Meteor
from match.live_match import LiveMatch

class LiveMatchGenerator:
    def __init__(self, meteor_db: Meteor):
        self._meteor_db = meteor_db

    def get_live_match(self, platform_id, game_id):
        db_match = self._meteor_db.get_db_match(platform_id, game_id)
        if db_match:
            return self._generate_live_match(db_match)

    def get_new_live_matches(self, younger_then:timedelta):
        db_matches = self._meteor_db.get_new_live_matches(
            younger_then
            )
        matches = []
        for db_match in db_matches:
            matches.append(self._generate_live_match(db_match))
        return matches

    def _generate_live_match(self, db_match):
        platform_id = db_match['platformId']
        game_id = db_match['gameId']
        encryption_key = db_match['observers']['encryptionKey']
        return LiveMatch(
            platform_id,
            game_id,
            encryption_key,
            self._meteor_db
            )