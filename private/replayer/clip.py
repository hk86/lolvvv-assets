from datetime import timedelta

class Clip:
    clip_path = ''
    clip_uri = ''
    length = timedelta()
    ingame_clip_num = 0
    event = None
    main_pros = []
    participant_pros = []
    victim_pros = []

    @property
    def id(self):
        return self.__hash__()

    def __hash__(self):
        if self.event:
            return hash((
                self.event.platform_id,
                self.event.game_id,
                self.event.ev_type,
                self.main_pros,
                self.event.start_time.total_seconds()))
