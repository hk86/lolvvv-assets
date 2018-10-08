from .match import Match
from kill_row import KillInRow

class Replay(Match):
    def __init__(self, live_match):
        Match.__init__(self,
                       live_match.platform_id,
                       live_match.game_id,
                       live_match.encryption_key)
        self._meteor_db = live_match.meteor_db

    def _set_state(self, status: str):
        self._meteor_db.set_replay_status(self, status)

    def _get_state(self):
        state = self._meteor_db.get_replay_status(self.game_id,
                                                  self.platform_id)
        if not state:
            state = 'invalid'
        return state

    state = property(fget=_get_state, fset=_set_state)
