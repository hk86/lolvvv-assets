from abc import ABC, abstractmethod
from match.replay import Replay

class ReplayService(ABC):
    @abstractmethod
    def init_replay(self, replay:Replay):
        pass

    @abstractmethod
    def add_data_chunk(self, replay:Replay, chunk_id, data_chunk):
        pass

    @abstractmethod
    def add_key_frame(self, replay:Replay, key_frame_id, key_frame):
        pass

    @abstractmethod
    def set_metas(self, replay:Replay, metas):
        pass

    @abstractmethod
    def delete_replay(self, replay:Replay):
        pass
    