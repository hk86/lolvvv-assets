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
        main_pro_ids = []
        for main_pro in clip.main_pros:
            main_pro_ids.append(main_pro.id)
        clip_entry = {
            'clipId': clip.id,
            'platformId': clip.event.platform_id,
            'gameId': clip.event.game_id,
            'eventType': clip.event.ev_type,
            'mainProIds': main_pro_ids,
            'assistingProIds': participant_ids,
            'opponentProIds': victim_ids,
            'eventsLength': clip.event.length.total_seconds(),
            'clipLength': clip.length.total_seconds(),
            'ingameStartTime': clip.event.start_time.total_seconds(),
            'events': clip.event.events,
            'uri': clip.clip_uri,
        }
        self._meteor_db.store_clip_entry(clip_entry)