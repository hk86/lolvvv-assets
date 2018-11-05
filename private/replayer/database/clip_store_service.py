from database.meteor import Meteor

from clip import Clip
from event import EventType

class ClipStoreService:
    def __init__(self, meteor_db):
        self._meteor_db = meteor_db

    def store(self, clip:Clip):
        clip_entry = {
            'platformId': clip.platform_id,
            'gameId': clip.game_id,
            'eventType': EventType.STRING[clip.event.ev_type],
            'mainProIds': [clip.main_pro.id],
            'participantProIds': [], # ToDo: for future features
            'opponentProIds': [], # ToDo: for future features
            'uri': clip.clip_uri,
            'length': clip.event.length.total_seconds()
        }
        self._meteor_db.store_clip_entry(clip_entry)