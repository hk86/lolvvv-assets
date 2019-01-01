from database.meteor import Meteor
from summoner.ingame_pro import IngamePro
from clip import Clip
from event import EventKillRow

from datetime import timedelta
import time

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
            'eventsLength': self._get_ts(clip.event.length),
            'clipLength': self._get_ts(clip.video.duration),
            'ingameStartTime': self._get_ts(clip.event.start_time),
            'clipAdded': self._get_ts(),
            'events': clip.event.events,
            'uri': clip.clip_uri,
            'matchPatch': '.'.join(clip.event.match_patch.split('.')[:2]),
            'counts': {
                'views': 0,
                'upVotes': 0,
                'downVotes': 0,
            }
        })

    def _get_ts(self, timestamp=None):
        if timestamp:
            ts_seconds = timestamp.total_seconds()
        else:
            ts_seconds = time.time()
        return int(ts_seconds*1000)

    def _prepare_ingame_pros(self, ingame_pros:[IngamePro]):
        pros = []
        for ingame_pro in ingame_pros:
            pros.append({
                'proId': ingame_pro.id,
                'championId': ingame_pro.champ_id,
            })
        return pros