from database.meteor import Meteor
from summoner.static_pro import StaticPro

class StaticProDb:
    def __init__(self, meteor_db):
        self._meteor_db = meteor_db

    def get_static_pro(self, account_id, platform_id):
        db_pro = self._meteor_db.get_pro(account_id, platform_id)
        if db_pro:
            return StaticPro(db_pro)