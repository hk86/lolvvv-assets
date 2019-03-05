from abc import ABC, abstractmethod
from clip import Clip


class ClipUploadService(ABC):
    @abstractmethod
    def upload(self, clip: Clip, callback_func):
        """
        :param clip: Clip that should be uploaded
        :type callback_func: function with clip as arguments
        """
        pass
