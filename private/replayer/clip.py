from hashlib import sha1

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
        id = sha1()
        id.update(self.event.platform_id.encode())
        id.update(str(self.event.game_id).encode())
        for pro in self.main_pros:
            id.update(str(pro.id).encode())
        id.update(str(self.event.start_time.total_seconds()).encode())
        return id.hexdigest()
