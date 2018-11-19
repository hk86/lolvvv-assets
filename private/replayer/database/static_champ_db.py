from database.meteor import Meteor

class StaticChampDb:
    def __init__(self, meteor: Meteor):
        self._meteor_db = meteor

    def get_champ_key(self, champ_id):
        champ_db = self._meteor_db.get_db_champ(champ_id)
        if champ_db:
            return champ_db['key']