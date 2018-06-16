from .database import Database

class MeteorDb(Database):

    def __init__(self, uri_meteor_db):
        Database.__init__(self, uri_meteor_db)