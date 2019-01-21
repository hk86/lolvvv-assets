from abc import ABC, abstractmethod
from datetime import timedelta

from database.kill import Kill


class CompanionFinderBase(ABC):

    def __init__(self, kills):
        self._kills = kills

    def find_companions(self, kill, companion_ids):
        companion_kills = []
        current_idx = self._get_kill_index(kill)
        kill_time_base = kill.timestamp
        while self._index_in_range(current_idx):
            current_idx = self._next_index(current_idx)
            candidate = self._kills[current_idx]
            time_distance = self._get_timedelta(candidate.timestamp,
                                                kill_time_base)
            if time_distance <= self._timeout:
                for comp_id in candidate.companion_ids:
                    if comp_id in companion_ids:
                        companion_kills.append(candidate)
                        kill_time_base = candidate.timestamp
                        break
                    else:
                        break
        companion_kills.sort(key=lambda x: x.timestamp)
        return companion_kills

    @property
    @abstractmethod
    def _timeout(self):
        pass

    def _get_kill_index(self, kill: Kill) -> int:
        for index, s_kill in enumerate(self._kills):
            if s_kill == kill:
                return index

    @staticmethod
    @abstractmethod
    def _get_timedelta(candidate_time, time_base):
        pass

    @abstractmethod
    def _index_in_range(self, index):
        pass

    @staticmethod
    @abstractmethod
    def _next_index(index):
        pass


"""
        ## pre
        current_idx = get_kill_index(event.first_kill, kills)
        kill_time_base = kills[current_idx].timestamp
        companion_kills_pre = []
        while current_idx > 0:
            current_idx = current_idx - 1
            candidate = kills[current_idx]
            time_distance = (kill_time_base - candidate.timestamp)
            if time_distance <= _PREPEND_TIMEOUT:
                for comp_id in candidate.companion_ids:
                    if comp_id in companion_ids:
                        companion_kills_pre.insert(0, candidate)
                        kill_time_base = candidate.timestamp
                        break
            else:
                break
"""


class CompanionPreFinder(CompanionFinderBase):
    _timeout = timedelta(seconds=5)

    @staticmethod
    def _index_in_range(index):
        return index > 0

    @staticmethod
    def _next_index(index):
        return index - 1

    @staticmethod
    def _get_timedelta(candidate_time, time_base):
        return time_base - candidate_time


"""

        current_idx = get_kill_index(event.last_kill, kills)
        kill_time_base = kills[current_idx].timestamp
        companion_kills_post = []
        while current_idx < (len(kills) - 1):
            current_idx = current_idx + 1
            candidate = kills[current_idx]
            time_distance = (candidate.timestamp - kill_time_base)
            if time_distance <= _POSTPEND_TIMEOUT:
                for comp_id in candidate.companion_ids:
                    if comp_id in companion_ids:
                        companion_kills_post.append(candidate)
                        kill_time_base = candidate.timestamp
                        break
            else:
                break
"""


class CompanionPostFinder(CompanionFinderBase):
    _timeout = timedelta(seconds=10)

    @staticmethod
    def _get_timedelta(candidate_time, time_base):
        return candidate_time - time_base

    def _index_in_range(self, index):
        return index < (len(self._kills) - 1)

    @staticmethod
    def _next_index(index):
        return index + 1
