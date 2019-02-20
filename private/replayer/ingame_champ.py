from abc import ABC, abstractmethod
from PIL import Image


class IngameChamp(ABC):
    size_y = 32
    _COORDINATE_Y_CHAMP1 = 876
    _COORDINATE_Y_OFFSET = 42

    def __init__(self, in_team_index: int, lol_screenshot: Image):
        self._in_team_index = in_team_index
        self._lol_screenshot = lol_screenshot

    @property
    def icon(self):
        crop_rectangle = (self.coordinate_x,
                          self.coordinate_y,
                          self.coordinate_x + self.size_x,
                          self.coordinate_y + self.size_y)
        return self._lol_screenshot.crop(crop_rectangle)

    @property
    @abstractmethod
    def team_id(self):
        pass

    @property
    @abstractmethod
    def coordinate_x(self):
        pass

    @property
    @abstractmethod
    def size_x(self):
        pass

    @property
    def in_team_idx(self):
        return self._in_team_index

    @property
    def coordinate_y(self):
        return self._COORDINATE_Y_CHAMP1 + \
               self._in_team_index * self._COORDINATE_Y_OFFSET


class BlueIngameChamp(IngameChamp):
    team_id = 100
    coordinate_x = 926
    size_x = 33


class RedIngameChamp(IngameChamp):
    team_id = 200
    coordinate_x = 975
    size_x = 32
