from collections import OrderedDict

from database.database import Database
from match.fact_match import FactMatch

class FactDataDb(Database):

    def __init__(self, uri_fact_db):
        Database.__init__(self, uri_fact_db)
        self._fact_matches = self._db['factdata']['matches']

    def get_fact_match(self, platform_id: str, game_id: int):
        fact_data = self._fact_matches.find_one(
            {'$and': [{'gameId': game_id},
                {'platformId':platform_id}]})
        if fact_data:
            return FactMatch(platform_id, game_id, fact_data)
        else:
            return None
