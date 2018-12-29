from database.meteor import Meteor
from summoner.ingame_pro import IngamePro
from clip import Clip
from event import EventKillRow

class ClipStoreService:
    def __init__(self, meteor_db):
        self._meteor_db = meteor_db

    def store(self, clip:Clip):
        self._meteor_db.store_clip_entry({
            'clipId': clip.id,
            'platformId': clip.event.platform_id,
            'gameId': clip.event.game_id,
            'eventType': clip.event.ev_type,
            'mainPros': self._prepare_ingame_pros(clip.main_pros),
            'assistingPros': self._prepare_ingame_pros(clip.participant_pros),
            'opponentPros': self._prepare_ingame_pros(clip.victim_pros),
            'eventsLength': clip.event.length.total_seconds(),
            'clipLength': clip.video.duration.total_seconds(),
            'ingameStartTime': clip.event.start_time.total_seconds(),
            'events': clip.event.events,
            'uri': clip.clip_uri,
            'count': {
                'view': 0,
                'upVotes': 0,
                'downVotes': 0,
            }
        })

    def _prepare_ingame_pros(self, ingame_pros:[IngamePro]):
        pros = []
        for ingame_pro in ingame_pros:
            pros.append({
                'proId': ingame_pro.id,
                'champId': ingame_pro.champ_id,
            })
        return pros