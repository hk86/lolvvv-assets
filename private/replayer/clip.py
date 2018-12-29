from hashlib import blake2b

from datetime import timedelta

class Clip:
    clip_uri = ''
    ingame_clip_num = 0
    event = None
    main_pros = []
    participant_pros = []
    victim_pros = []
    video = None

    @property
    def id(self, len_id=16):
        id = blake2b(digest_size=int(len_id/2))
        id.update(self.event.platform_id.encode())
        id.update(str(self.event.game_id).encode())
        for pro in self.main_pros:
            id.update(str(pro.id).encode())
        id.update(str(self.event.start_time.total_seconds()).encode())
        return id.hexdigest()
