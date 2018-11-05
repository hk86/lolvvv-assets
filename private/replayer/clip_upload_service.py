from abc import ABC, abstractmethod
from clip import Clip

class ClipUploadService(ABC):
    @abstractmethod
    def upload(self, clip: Clip, callback_func):
        pass