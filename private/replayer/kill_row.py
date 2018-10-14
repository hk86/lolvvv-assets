
class KillRow:
    SINGLE_KILL = 1
    DOUBLE_KILL = 2
    TRIPPLE_KILL = 3
    QUADRA_KILL = 4
    PENTA_KILL = 5

    def __init__(self, row: list):
        self._kill_row = row

    def row_length(self):
        return len(self._kill_row)

    def first_kill_ingame_time(self):
        return self._kill_row[0].timestamp

    def kill_row_time(self):
        row_length = len(self._kill_row)
        last_kill_time = self._kill_row[row_length-1].timestamp
        return (last_kill_time-self.first_kill_ingame_time())

    def killer(self):
        return self._kill_row[0].killer

    #first_kill_ingame_time = property(fget=_get_first_kill_ingame_time)