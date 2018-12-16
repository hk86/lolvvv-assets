from abc import ABC, abstractmethod

class Spectate(ABC):

    def __init__(self, encryption_key, url):
        self._ENCRYPTION_KEY = encryption_key
        self._URL = url

    @property
    def encryption_key(self):
        return self._ENCRYPTION_KEY

    @property
    def url(self):
        return self._URL