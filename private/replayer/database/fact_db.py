from datetime import datetime, timedelta, timezone

from database.database import Database
from database.kill import Kill

class FactDataDb(Database):

    def __init__(self, uri_fact_db):
        Database.__init__(self, uri_fact_db)
        self._fact_matches = self._db['factdata']['matches']
        self._match_cached = None

    def _match_factdata(self, gameId, platformId):
        if ((self._match_cached == None) or
            (self._match_cached['gameId'] != gameId) or
            (self._match_cached['platformId'] != platformId)):
            self._match_cached = self._fact_matches.find_one(
                {'$and': [{'gameId': gameId},
                {'platformId':platformId}]})
        return self._match_cached

    def get_match_kills(self, gameId, platformId):
        matchFactdata = self._match_factdata(gameId, platformId)
        kills = []
        for frame in matchFactdata['timeline']['frames']:
            for event in frame['events']:
                if event['type'] == 'CHAMPION_KILL':
                    print(event)
                    kills.append(Kill(event))
        return kills
