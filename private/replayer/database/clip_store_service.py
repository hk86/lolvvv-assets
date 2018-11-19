from database.meteor import Meteor
from clip import Clip
from event import EventKillRow

class ClipStoreService:
    def __init__(self, meteor_db):
        self._meteor_db = meteor_db

    def store(self, clip:Clip):
        participant_ids = []
        for participant_pro in clip.participant_pros:
            participant_ids.append(participant_pro.id)
        victim_ids = []
        for victim_pro in clip.victim_pros:
            victim_ids.append(victim_pro.id)
        clip_entry = {
            'platformId': clip.platform_id,
            'gameId': clip.game_id,
            'eventType': clip.event.ev_type,
            'mainProIds': [clip.main_pro.id],
            'assistingProIds': participant_ids,
            'opponentProIds': victim_ids,
            'uri': clip.clip_uri,
            'length': clip.event.length.total_seconds()
        }
        self._meteor_db.store_clip_entry(clip_entry)