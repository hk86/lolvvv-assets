from collections import OrderedDict

from database.database import Database
from match.fact_match import FactMatch

class FactDataDb(Database):

    def __init__(self, uri_fact_db):
        Database.__init__(self, uri_fact_db)
        self._fact_matches = self._db['factdata']['matches']
        self._match_cached = None

    def get_fact_match(self, platform_id: str, game_id: int):
        if ((self._match_cached == None) or
            (self._match_cached.game_id != game_id) or
            (self._match_cached.platform_id != platform_id)):
            fact_data = self._fact_matches.find_one(
                OrderedDict([
                    ('platformId', platform_id),
                    ('gameId', game_id),
                ])
            )
            if fact_data:
                self._match_cached = FactMatch(platform_id, game_id, fact_data)
            else:
                return None
        return self._match_cached
