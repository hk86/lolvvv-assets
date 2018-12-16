from abc import ABC, abstractmethod
from match.spectate_match import SpectateMatch

class ReplayService(ABC):
    @abstractmethod
    def init_replay(self, replay:SpectateMatch):
        pass

    @abstractmethod
    def add_data_chunk(self, replay:SpectateMatch, chunk_id, data_chunk):
        pass

    @abstractmethod
    def add_key_frame(self, replay:SpectateMatch, key_frame_id, key_frame):
        pass

    @abstractmethod
    def set_metas(self, replay:SpectateMatch, metas):
        pass

    @abstractmethod
    def delete_replay(self, replay:SpectateMatch):
        pass
    